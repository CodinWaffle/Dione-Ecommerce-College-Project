"""
Main routes for Dione Ecommerce
"""
from flask import Blueprint, render_template, jsonify, redirect, url_for, flash, current_app, session
from flask import request
from flask_login import login_required, current_user, logout_user
from project import db
from project.models import Product, User, SellerProduct, ProductReport, Seller, CartItem, Order, OrderItem

from sqlalchemy import func
import hashlib
import json
import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from collections import defaultdict

main = Blueprint('main', __name__)

MAX_CART_ITEM_QUANTITY = 100

def generate_color_from_name(color_name):
    """Generate a consistent color hex from a color name"""
    if not color_name:
        return '#000000'
    
    # Common color mappings
    color_map = {
        'red': '#FF0000',
        'blue': '#0000FF', 
        'green': '#008000',
        'yellow': '#FFFF00',
        'orange': '#FFA500',
        'purple': '#800080',
        'pink': '#FFC0CB',
        'brown': '#A52A2A',
        'black': '#000000',
        'white': '#FFFFFF',
        'gray': '#808080',
        'grey': '#808080',
        'navy': '#000080',
        'maroon': '#800000',
        'olive': '#808000',
        'lime': '#00FF00',
        'aqua': '#00FFFF',
        'teal': '#008080',
        'silver': '#C0C0C0',
        'fuchsia': '#FF00FF',
    }
    
    # Check for exact matches first
    name_lower = color_name.lower().strip()
    if name_lower in color_map:
        return color_map[name_lower]
    
    # Check for partial matches
    for color, hex_val in color_map.items():
        if color in name_lower:
            return hex_val
    
    # Generate a consistent color from the name using hash
    hash_obj = hashlib.md5(color_name.encode())
    hash_hex = hash_obj.hexdigest()
    
    # Use first 6 characters as color, but ensure it's not too dark
    r = int(hash_hex[0:2], 16)
    g = int(hash_hex[2:4], 16) 
    b = int(hash_hex[4:6], 16)
    
    # Ensure minimum brightness
    if r + g + b < 200:
        r = min(255, r + 100)
        g = min(255, g + 100)
        b = min(255, b + 100)
    
    return f'#{r:02x}{g:02x}{b:02x}'


def _normalize_image_path(path):
    """Normalize stored image path into a usable URL for the frontend.

    If `path` is an absolute URL or already starts with `/`, return as-is.
    Otherwise prefix with `/static/` so static files under `static/` are reachable.
    """
    if not path:
        return None
    s = str(path)
    if s.startswith('data:'):
        return s
    if s.startswith('/') or s.startswith('http'):
        return s
    return '/static/' + s.lstrip('/')


def _extract_image_value(image_value):
    """Extract a usable string path from nested image structures."""
    if not image_value:
        return None

    if isinstance(image_value, list):
        for entry in image_value:
            resolved = _extract_image_value(entry)
            if resolved:
                return resolved
        return None

    if isinstance(image_value, dict):
        for key in ('url', 'path', 'src', 'image', 'image_url', 'value', 'file'):
            if key in image_value and image_value[key]:
                resolved = _extract_image_value(image_value[key])
                if resolved:
                    return resolved
        return None

    if isinstance(image_value, bytes):
        try:
            image_value = image_value.decode('utf-8')
        except Exception:
            return None

    if isinstance(image_value, str):
        stripped = image_value.strip().strip('"')
        if not stripped:
            return None
        if (stripped.startswith('[') and stripped.endswith(']')) or (
            stripped.startswith('{') and stripped.endswith('}')
        ):
            try:
                parsed = json.loads(stripped)
                return _extract_image_value(parsed)
            except Exception:
                pass
        return stripped

    return str(image_value)


def _resolve_image_source(*sources, default='/static/image/banner_1.png'):
    """Return the first normalized image path from the provided sources."""
    for src in sources:
        resolved = _extract_image_value(src)
        if not resolved:
            continue
        normalized = _normalize_image_path(resolved)
        if normalized:
            return normalized
    return default


def _parse_variants_structure(raw_variants):
    """Return variants data parsed from potential JSON strings."""
    if not raw_variants:
        return None
    if isinstance(raw_variants, str):
        try:
            return json.loads(raw_variants)
        except Exception:
            return None
    return raw_variants


def _find_variant_by_color(variants_data, color_name):
    """Locate a variant entry (dict) matching the provided color name."""
    if not variants_data or not color_name:
        return None

    normalized_color = str(color_name).strip().lower()

    if isinstance(variants_data, dict):
        for key, variant_info in variants_data.items():
            if str(key).strip().lower() == normalized_color:
                return variant_info
    elif isinstance(variants_data, list):
        for variant_info in variants_data:
            if not isinstance(variant_info, dict):
                continue
            variant_color = (
                variant_info.get('color')
                or variant_info.get('color_name')
                or variant_info.get('variant_name')
                or variant_info.get('variantName')
                or variant_info.get('name')
            )
            if variant_color and str(variant_color).strip().lower() == normalized_color:
                return variant_info
    return None


def _build_stock_map_from_variant(variant_info):
    """Extract a {size_label: stock_count} mapping from assorted variant schemas."""
    stock_map = {}
    if not isinstance(variant_info, dict):
        return stock_map

    raw_stock = variant_info.get('stock')
    if isinstance(raw_stock, dict):
        stock_map.update(raw_stock)
    elif raw_stock is not None and variant_info.get('size'):
        stock_map[variant_info.get('size')] = raw_stock

    size_stocks = variant_info.get('sizeStocks') or variant_info.get('sizes')
    if isinstance(size_stocks, list):
        for entry in size_stocks:
            if not isinstance(entry, dict):
                continue
            size_label = (
                entry.get('size')
                or entry.get('size_label')
                or entry.get('label')
                or entry.get('name')
            )
            stock_value = (
                entry.get('stock')
                or entry.get('quantity')
                or entry.get('qty')
                or entry.get('value')
            )
            if size_label:
                stock_map[size_label] = stock_value

    return stock_map


def _iter_variant_entries(variants_data):
    """Yield (color_name, variant_info) tuples from dict or list variant structures."""
    if isinstance(variants_data, dict):
        for key, value in variants_data.items():
            yield key, value
    elif isinstance(variants_data, list):
        for idx, entry in enumerate(variants_data, start=1):
            if not isinstance(entry, dict):
                continue
            color_name = (
                entry.get('color')
                or entry.get('color_name')
                or entry.get('variant_name')
                or entry.get('variantName')
                or entry.get('name')
                or f"Variant {idx}"
            )
            yield color_name, entry


def _extract_variant_images(variant_info):
    """Return raw image data stored on a variant entry regardless of schema."""
    if not isinstance(variant_info, dict):
        return None
    return (
        variant_info.get('images')
        or variant_info.get('image')
        or variant_info.get('imageUrls')
        or variant_info.get('photos')
        or variant_info.get('gallery')
    )


def _generate_cart_item_sku(product, color=None, size=None, fallback=None):
    """Generate a readable SKU for cart display without requiring a DB column."""
    if fallback:
        return fallback

    base = None
    try:
        base = (product.base_sku if product else None) or getattr(product, 'sku', None)
    except Exception:
        base = None

    if base:
        base = str(base).strip()

    if not base:
        if product and getattr(product, 'id', None):
            base = f"SKU{product.id}"
        else:
            base = 'SKU'

    parts = [base]
    if color:
        parts.append(str(color).strip().upper().replace(' ', ''))
    if size:
        parts.append(str(size).strip().upper())

    return '-'.join([p for p in parts if p])


@main.before_request
def check_suspension():
    """Check if authenticated user is suspended and log them out if needed"""
    if current_user.is_authenticated and getattr(current_user, 'is_suspended', False):
        logout_user()
        flash('Your account has been suspended. Please contact support.', 'danger')
        return redirect(url_for('auth.login'))

@main.route('/')
def index():
    # If a pending seller/rider logs in, force pending page until approved
    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
        if getattr(current_user, 'role_requested', None) and not getattr(current_user, 'is_approved', True):
            return redirect(url_for('main.pending'))
        role = (getattr(current_user, 'role', '') or '').lower()
        if role == 'seller':
            return redirect(url_for('seller.dashboard'))
        if role == 'rider':
            return redirect(url_for('main.rider_dashboard'))
    
    # Navigation items for header
    nav_items = get_nav_items()
    
    # Get products from both models
    featured = Product.query.filter_by(status='active').order_by(Product.created_at.desc()).limit(4).all()
    trending = Product.query.filter_by(status='active').order_by(Product.stock.desc()).limit(4).all()
    new_arrivals = Product.query.filter_by(status='active').order_by(Product.updated_at.desc()).limit(4).all()
    
    # Get seller products
    seller_featured = SellerProduct.query.filter_by(status='active').order_by(SellerProduct.created_at.desc()).limit(4).all()
    seller_trending = SellerProduct.query.filter_by(status='active').order_by(SellerProduct.total_stock.desc()).limit(4).all()
    seller_new_arrivals = SellerProduct.query.filter_by(status='active').order_by(SellerProduct.updated_at.desc()).limit(4).all()

    def seller_to_public_dict(sp):
        return {
            'id': sp.id,
            'name': sp.name,
            'primaryImage': _normalize_image_path(sp.primary_image) or '/static/image/banner_1.png',
            'secondaryImage': _normalize_image_path(sp.secondary_image) or _normalize_image_path(sp.primary_image) or '/static/image/banner_1.png',
            'material': (sp.materials or 'Premium Material').split('\n')[0] if sp.materials else 'Premium Material',
            'price': float(sp.price or 0),
            'originalPrice': float(sp.compare_at_price) if sp.compare_at_price and sp.compare_at_price > sp.price else None,
            'category': sp.category,
            'subcategory': sp.subcategory,
        }

    product_buckets = {
        'featured': [product.to_public_dict() for product in featured] + [seller_to_public_dict(sp) for sp in seller_featured],
        'trending': [product.to_public_dict() for product in trending] + [seller_to_public_dict(sp) for sp in seller_trending],
        'new_arrivals': [product.to_public_dict() for product in new_arrivals] + [seller_to_public_dict(sp) for sp in seller_new_arrivals],
    }
    
    return render_template('main/index.html', nav_items=nav_items, product_buckets=product_buckets)


@main.route('/api/products')
def api_products():
    """API: Return active products from both Product and SellerProduct models.

    Query params:
      - category (optional)
      - subcategory (optional)
      - limit (optional)
    """
    try:
        category = request.args.get('category')
        subcategory = request.args.get('subcategory')
        limit = int(request.args.get('limit') or 48)
    except Exception:
        category = None
        subcategory = None
        limit = 48

    # Fetch from Product model (legacy products)
    q1 = Product.query.filter(func.lower(Product.status) == 'active')
    if category:
        try:
            q1 = q1.filter(func.lower(Product.category) == category.lower())
        except Exception:
            q1 = q1.filter(Product.category == category)
    if subcategory:
        try:
            q1 = q1.filter(func.lower(Product.subcategory) == subcategory.lower())
        except Exception:
            q1 = q1.filter(Product.subcategory == subcategory)
    
    # Fetch from SellerProduct model (seller-created products)
    q2 = SellerProduct.query.filter(func.lower(SellerProduct.status) == 'active')
    if category:
        try:
            q2 = q2.filter(func.lower(SellerProduct.category) == category.lower())
        except Exception:
            q2 = q2.filter(SellerProduct.category == category)
    if subcategory:
        try:
            q2 = q2.filter(func.lower(SellerProduct.subcategory) == subcategory.lower())
        except Exception:
            q2 = q2.filter(SellerProduct.subcategory == subcategory)
    
    # Get products from both models
    products = q1.order_by(Product.updated_at.desc()).limit(limit // 2).all()
    seller_products = q2.order_by(SellerProduct.updated_at.desc()).limit(limit // 2).all()
    
    # Convert to public dict format
    items = []
    for p in products:
        # Ensure Product.image is normalized for frontend
        pd = p.to_public_dict()
        if pd.get('primaryImage'):
            # if database stored path lacks /static prefix, normalize it
            if not (str(pd.get('primaryImage')).startswith('/') or str(pd.get('primaryImage')).startswith('http')):
                pd['primaryImage'] = _normalize_image_path(pd['primaryImage'])
        if pd.get('secondaryImage'):
            if not (str(pd.get('secondaryImage')).startswith('/') or str(pd.get('secondaryImage')).startswith('http')):
                pd['secondaryImage'] = _normalize_image_path(pd['secondaryImage'])
        items.append(pd)
    
    for sp in seller_products:
        # Convert SellerProduct to public dict format compatible with frontend
        items.append({
            'id': sp.id,
            'name': sp.name,
            'primaryImage': _normalize_image_path(sp.primary_image) or '/static/image/banner_1.png',
            'secondaryImage': _normalize_image_path(sp.secondary_image) or _normalize_image_path(sp.primary_image) or '/static/image/banner_1.png',
            'material': (sp.materials or 'Premium Material').split('\n')[0] if sp.materials else 'Premium Material',
            'price': float(sp.price or 0),
            'originalPrice': float(sp.compare_at_price) if sp.compare_at_price and sp.compare_at_price > sp.price else None,
            'category': sp.category,
            'subcategory': sp.subcategory,
        })
    
    # Sort combined results by most recent and limit
    items = sorted(items, key=lambda x: x.get('id', 0), reverse=True)[:limit]
    
    return jsonify({'products': items, 'count': len(items)})


@main.route('/api/product/<int:product_id>/variant/<variant_id>')
def api_product_variant(product_id, variant_id):
    """Return variant-specific data for AJAX updates."""
    try:
        sp = SellerProduct.query.get(product_id)
        if not sp or not sp.variants:
            return jsonify({'error': 'Product or variant not found'}), 404
            
        # Find the specific variant
        # Parse variants if it's a string
        variants_data = sp.variants
        if isinstance(variants_data, str):
            import json
            try:
                variants_data = json.loads(variants_data)
            except (json.JSONDecodeError, TypeError):
                variants_data = []
        
        if isinstance(variants_data, list):
            variant = None
            for v in variants_data:
                if str(v.get('color', '')) == str(variant_id):
                    variant = v
                    break
            
            if not variant:
                return jsonify({'error': 'Variant not found'}), 404
                
            return jsonify({
                'variant': {
                    'color': variant.get('color'),
                    'images': {
                        'primary': _normalize_image_path(sp.primary_image) or '/static/image/banner_1.png',
                        'secondary': _normalize_image_path(sp.secondary_image) or _normalize_image_path(sp.primary_image) or '/static/image/banner_1.png'
                    },
                    'stock': {variant.get('size', 'OS'): variant.get('stock', 0)}
                }
            })
        
        return jsonify({'error': 'Invalid variant structure'}), 400
    except Exception as e:
        return jsonify({'error': 'Server error', 'detail': str(e)}), 500

@main.route('/api/product/<int:product_id>')
def api_product(product_id):
    """Return a single product (Product or SellerProduct) as JSON for client-side detail updates."""
    try:
        # Try SellerProduct first (more detailed)
        sp = SellerProduct.query.get(product_id)
        if sp:
            # Build variant_photos and stock_data from variants JSON
            variant_photos = {}
            stock_data = {}
            try:
                # Parse variants if it's a string
                variants_data = sp.variants
                if isinstance(variants_data, str):
                    import json
                    try:
                        variants_data = json.loads(variants_data)
                    except (json.JSONDecodeError, TypeError):
                        variants_data = []
                
                if isinstance(variants_data, list):
                    # Convert list of variants to structured data
                    for variant in variants_data:
                        if isinstance(variant, dict):
                            color = variant.get('color', 'Unknown')
                            # variant may define a single size/stock or a list of sizeStocks
                            size = variant.get('size', 'OS')
                            stock = variant.get('stock', 0)
                            size_stocks = variant.get('sizeStocks')
                            color_hex = variant.get('colorHex', '#000000')
                            
                            # Initialize color in stock_data if not exists
                            if color not in stock_data:
                                stock_data[color] = {}
                            
                            # If variant provides per-size stocks, use those to populate stock_data
                            if isinstance(size_stocks, list) and size_stocks:
                                for ss in size_stocks:
                                    try:
                                        sname = ss.get('size') if isinstance(ss, dict) else None
                                        sval = int(ss.get('stock', 0)) if isinstance(ss, dict) else 0
                                        if sname:
                                            stock_data[color][sname] = sval
                                    except Exception:
                                        continue
                            else:
                                # Add single size stock for this color
                                stock_data[color][size] = stock
                            
                            # Set color hex for styling (store in variant_photos for now)
                            if color not in variant_photos:
                                variant_photos[color] = {
                                    'primary': _normalize_image_path(sp.primary_image) or '/static/image/banner_1.png',
                                    'secondary': _normalize_image_path(sp.secondary_image) or _normalize_image_path(sp.primary_image) or '/static/image/banner_1.png',
                                    'color_hex': color_hex
                                }
                elif isinstance(variants_data, dict):
                    # Handle existing dict structure
                    for k, v in variants_data.items():
                        # v might be { 'images': [...], 'stock': { 'XS': 3, ... } }
                        if isinstance(v, dict):
                            if 'images' in v and v['images']:
                                primary = v['images'][0]
                                secondary = v['images'][1] if len(v['images']) > 1 else None
                                variant_photos[k] = {'primary': primary, 'secondary': secondary}
                            if 'stock' in v and isinstance(v['stock'], dict):
                                stock_data[k] = v['stock']
                        elif isinstance(v, list):
                            # list of images
                            variant_photos[k] = {'primary': v[0], 'secondary': v[1] if len(v) > 1 else None}
            except Exception:
                variant_photos = {}
                stock_data = {}

            # fallback to top-level images with proper normalization
            primary = _normalize_image_path(sp.primary_image) or '/static/image/banner_1.png'
            secondary = _normalize_image_path(sp.secondary_image) or _normalize_image_path(sp.primary_image) or '/static/image/banner_1.png'

            payload = {
                'id': sp.id,
                'name': sp.name,
                'description': sp.description,
                'price': float(sp.price or 0),
                'originalPrice': float(sp.compare_at_price) if sp.compare_at_price and sp.compare_at_price > sp.price else None,
                'primaryImage': primary,
                'secondaryImage': secondary,
                'materials': sp.materials,
                'details_fit': sp.details_fit,
                'variants': variants_data or {},
                'variant_photos': variant_photos,
                'stock_data': stock_data,
                'type': 'seller'
            }
            return jsonify({'product': payload})



        @main.route('/api/product/<int:product_id>/report', methods=['POST'])
        def api_report_product(product_id):
            """Accept a report/flag for a product and save it to the database.

            Expected JSON: { reason: 'inappropriate'|'spam'|..., details: 'optional details' }
            """
            try:
                data = request.get_json(force=True, silent=True) or request.form or {}
                reason = (data.get('reason') or request.values.get('reason') or '').strip()
                details = data.get('details') or request.values.get('details') or ''

                if not reason:
                    return jsonify({'error': 'Reason is required'}), 400

                reporter_id = None
                try:
                    if current_user and getattr(current_user, 'is_authenticated', False):
                        reporter_id = current_user.id
                except Exception:
                    reporter_id = None

                report = ProductReport(product_id=product_id, reporter_id=reporter_id, reason=reason, details=details)
                db.session.add(report)
                db.session.commit()

                return jsonify({'success': True, 'report_id': report.id}), 201
            except Exception as e:
                db.session.rollback()
                return jsonify({'error': 'Server error', 'detail': str(e)}), 500

        # Try legacy Product model
        p = Product.query.get(product_id)
        if p:
            payload = p.to_public_dict()
            payload.update({
                'description': p.description,
                'materials': p.materials,
                'details_fit': getattr(p, 'details_fit', None),
                'variant_photos': {},
                'stock_data': {},
                'type': 'legacy'
            })
            return jsonify({'product': payload})

        return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        return jsonify({'error': 'Server error', 'detail': str(e)}), 500


@main.route('/homepage')
def homepage():
    """Lightweight homepage route that renders the standalone homepage.html template
    and provides `new_arrivals` products for client-side rendering.
    """
    nav_items = get_nav_items()
    
    # Get new arrivals from both models
    new_arrivals_q = Product.query.filter_by(status='active').order_by(Product.updated_at.desc()).limit(4).all()
    seller_new_arrivals_q = SellerProduct.query.filter_by(status='active').order_by(SellerProduct.updated_at.desc()).limit(4).all()
    
    new_arrivals = []
    
    # Add products from Product model
    for p in new_arrivals_q:
        d = p.to_public_dict()
        # include rating if the model has it (safe getattr)
        d['rating'] = getattr(p, 'rating', None)
        new_arrivals.append(d)
    
    # Add products from SellerProduct model
    for sp in seller_new_arrivals_q:
        d = {
            'id': sp.id,
            'name': sp.name,
            'primaryImage': sp.primary_image or '/static/image/banner_1.png',
            'secondaryImage': sp.secondary_image or sp.primary_image or '/static/image/banner_1.png',
            'material': (sp.materials or 'Premium Material').split('\n')[0] if sp.materials else 'Premium Material',
            'price': float(sp.price or 0),
            'originalPrice': float(sp.compare_at_price) if sp.compare_at_price and sp.compare_at_price > sp.price else None,
            'category': sp.category,
            'subcategory': sp.subcategory,
            'rating': None  # SellerProduct doesn't have rating field yet
        }
        new_arrivals.append(d)

    return render_template('main/homepage.html', nav_items=nav_items, new_arrivals=new_arrivals)

@main.route('/profile')
@login_required
def profile():
    role = (getattr(current_user, 'role', '') or 'buyer').lower()
    if getattr(current_user, 'role_requested', None) and not getattr(current_user, 'is_approved', True):
        return redirect(url_for('main.pending'))
    if role == 'seller':
        return redirect(url_for('seller.dashboard'))
    if role == 'rider':
        return redirect(url_for('main.rider_dashboard'))
    return render_template('main/profile.html', username=current_user.email)

# Seller routes moved to seller_routes.py blueprint

@main.route('/rider/dashboard')
@login_required
def rider_dashboard():
    if (getattr(current_user, 'role', '') or '').lower() != 'rider' or not getattr(current_user, 'is_approved', False):
        flash("You don't have access to the rider dashboard.", 'warning')
        return redirect(url_for('main.profile'))
    return render_template('rider/rider_dashboard.html', username=current_user.email)

@main.route('/rider/deliveries')
@login_required
def rider_deliveries():
    if (getattr(current_user, 'role', '') or '').lower() != 'rider':
        flash("You don't have access to rider tools.", 'warning')
        return redirect(url_for('main.profile'))
    # Placeholder deliveries page - replace with real delivery management later
    return render_template('rider/deliveries.html', username=current_user.email)

@main.route('/pending')
@login_required
def pending():
    """Show pending approval page for users awaiting role upgrade."""
    if getattr(current_user, 'role_requested', None) and not getattr(current_user, 'is_approved', True):
        return render_template('main/pending.html', username=current_user.email, requested=current_user.role_requested)
    # If not pending anymore, route to appropriate place
    role = (getattr(current_user, 'role', '') or 'buyer').lower()
    if role == 'seller':
        return redirect(url_for('seller.dashboard'))
    if role == 'rider':
        return redirect(url_for('main.rider_dashboard'))
    return redirect(url_for('main.index'))

@main.route('/cart')
def cart():
    """Display shopping cart with items grouped by store"""
    from flask import session
    nav_items = get_nav_items()

    raw_items = []
    session_items = session.get('cart_items', [])

    def _cart_item_sort_key(item):
        """Return a datetime for ordering cart entries (newest first)."""
        ts = item.get('added_at') or item.get('created_at')
        if isinstance(ts, datetime):
            return ts
        if not ts:
            return datetime.min
        try:
            ts_str = str(ts).strip()
            if ts_str.endswith('Z'):
                ts_str = ts_str[:-1] + '+00:00'
            return datetime.fromisoformat(ts_str)
        except Exception:
            return datetime.min

    if current_user.is_authenticated:
        db_items = (
            CartItem.query
            .filter_by(user_id=current_user.id)
            .order_by(CartItem.created_at.desc())
            .all()
        )
        raw_items = [item.to_dict() for item in db_items]

        # Merge any lingering session items (guest cart before login)
        if session_items:
            existing_keys = {
                (item.get('product_id'), item.get('color'), item.get('size'))
                for item in raw_items
            }
            for s_item in session_items:
                key = (s_item.get('product_id'), s_item.get('color'), s_item.get('size'))
                if key not in existing_keys:
                    raw_items.append(s_item)
    else:
        raw_items = session_items

    # Ensure newest additions appear first
    raw_items = sorted(raw_items, key=_cart_item_sort_key, reverse=True)

    cart_items = []
    subtotal = 0
    total_items = 0

    for item in raw_items:
        try:
            product = SellerProduct.query.get(item.get('product_id'))
            seller_user = User.query.get(product.seller_id) if product else None
            seller_profile = seller_user.seller_profile[0] if seller_user and seller_user.seller_profile else None
            store_name = seller_profile.business_name if seller_profile else 'Dione Store'

            price = float(item.get('product_price') or item.get('price') or 0)
            quantity = int(item.get('quantity') or 1)
            item_subtotal = price * quantity
            subtotal += item_subtotal
            total_items += quantity

            image_url = (
                item.get('variant_image')
                or item.get('image_url')
                or (product and _normalize_image_path(product.primary_image))
                or '/static/image/banner_1.png'
            )

            cart_items.append({
                'id': item.get('id') or f"{item.get('product_id')}_{item.get('color')}_{item.get('size')}",
                'product_id': item.get('product_id'),
                'name': item.get('product_name') or (product.name if product else 'Product'),
                'sku': _generate_cart_item_sku(product, item.get('color'), item.get('size'), item.get('sku')),
                'price': price,
                'quantity': quantity,
                'color': item.get('color') or 'Default',
                'size': item.get('size') or 'One Size',
                'image_url': image_url,
                'store_name': store_name,
                'subtotal': round(item_subtotal, 2),
                'max_quantity': MAX_CART_ITEM_QUANTITY
            })
        except Exception as e:
            print(f"Error processing cart item: {e}")
            continue

    # Group items by store for UI organization
    store_groups = []
    if cart_items:
        store_lookup = {}
        for item in cart_items:
            store_key = item.get('store_name', 'Dione Store')
            if store_key not in store_lookup:
                group = {
                    'store_name': store_key,
                    'items_list': [],
                    'item_count': 0
                }
                store_lookup[store_key] = group
                store_groups.append(group)

            group = store_lookup[store_key]
            group['items_list'].append(item)
            group['item_count'] += 1

    discount = 0  # Apply promo logic later
    delivery_fee = 0 if subtotal >= 1500 or subtotal == 0 else 150
    total = subtotal - discount + delivery_fee

    return render_template(
        'main/cart.html',
        nav_items=nav_items,
        cart_items=cart_items,
        store_groups=store_groups,
        total_items=total_items,
        subtotal=subtotal,
        discount=discount,
        delivery_fee=delivery_fee,
        total=total,
        max_cart_quantity=MAX_CART_ITEM_QUANTITY
    )


@main.route('/api/products/<int:product_id>/colors/<color_name>/sizes')
def get_sizes_for_color(product_id, color_name):
    """API endpoint to get available sizes for a specific product color"""
    try:
        from flask import jsonify
        from project.models import SellerProduct, ProductVariant, VariantSize
        
        # Get the product
        product = SellerProduct.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Initialize response data
        response_data = {
            'product_id': product_id,
            'color_name': color_name,
            'sizes': []
        }
        
        # Method 1: Try to get from ProductVariant and VariantSize tables (new structure)
        variant = ProductVariant.query.filter_by(
            product_id=product_id,
            variant_name=color_name
        ).first()
        
        if variant:
            # Get sizes from VariantSize table
            variant_sizes = VariantSize.query.filter_by(variant_id=variant.id).all()
            for size in variant_sizes:
                response_data['sizes'].append({
                    'variant_id': variant.id,
                    'size_id': size.id,
                    'size_label': size.size_label,
                    'stock': size.stock_quantity,
                    'sku': size.sku or f"{product.base_sku or 'P'}{product_id}-{color_name}-{size.size_label}",
                    'available': size.stock_quantity > 0
                })
        else:
            # Method 2: Fallback to variants JSON structure (legacy)
            try:
                variants_data = _parse_variants_structure(product.variants)
                color_variant = _find_variant_by_color(variants_data, color_name)

                if color_variant:
                    stock_info = _build_stock_map_from_variant(color_variant)
                    for size_label, stock_count in stock_info.items():
                        try:
                            stock_value = int(stock_count)
                        except Exception:
                            stock_value = int(float(stock_count) if stock_count else 0)

                        response_data['sizes'].append({
                            'variant_id': None,  # No variant_id for legacy structure
                            'size_id': None,
                            'size_label': size_label,
                            'stock': stock_value,
                            'sku': f"{product.base_sku or 'P'}{product_id}-{color_name}-{size_label}",
                            'available': stock_value > 0
                        })

            except Exception as e:
                print(f"Error parsing variants JSON: {e}")
        
        # Sort sizes by common size order
        size_order = {'XS': 1, 'S': 2, 'M': 3, 'L': 4, 'XL': 5, 'XXL': 6, '2XL': 6, '3XL': 7}
        response_data['sizes'].sort(key=lambda x: size_order.get(x['size_label'], 999))
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error in get_sizes_for_color: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500

@main.route('/api/products/<int:product_id>/variants')
def get_product_variants(product_id):
    """API endpoint to get all variants for a product"""
    try:
        from flask import jsonify
        from project.models import SellerProduct, ProductVariant, VariantSize
        
        # Get the product
        product = SellerProduct.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        response_data = {
            'product_id': product_id,
            'variants': []
        }
        
        # Method 1: Try ProductVariant table (new structure)
        variants = ProductVariant.query.filter_by(product_id=product_id).all()
        
        if variants:
            for variant in variants:
                variant_data = {
                    'variant_id': variant.id,
                    'color_name': variant.variant_name,
                    'color_hex': '#000000',  # Default, could be stored in variant
                    'images': variant.images_json or [],
                    'sizes': []
                }
                
                # Get sizes for this variant
                sizes = VariantSize.query.filter_by(variant_id=variant.id).all()
                for size in sizes:
                    variant_data['sizes'].append({
                        'size_id': size.id,
                        'size_label': size.size_label,
                        'stock': size.stock_quantity,
                        'sku': size.sku,
                        'available': size.stock_quantity > 0
                    })
                
                response_data['variants'].append(variant_data)
        else:
            # Method 2: Fallback to variants JSON (legacy)
            try:
                variants_data = _parse_variants_structure(product.variants)
                for color_name, variant_info in _iter_variant_entries(variants_data):
                    if not isinstance(variant_info, dict):
                        continue

                    variant_data = {
                        'variant_id': None,
                        'color_name': color_name,
                        'color_hex': variant_info.get('hex', '#000000'),
                        'images': _extract_variant_images(variant_info) or [],
                        'sizes': []
                    }

                    stock_info = _build_stock_map_from_variant(variant_info)
                    for size_label, stock_count in stock_info.items():
                        try:
                            stock_value = int(stock_count)
                        except Exception:
                            stock_value = int(float(stock_count) if stock_count else 0)

                        variant_data['sizes'].append({
                            'size_id': None,
                            'size_label': size_label,
                            'stock': stock_value,
                            'sku': f"{product.base_sku or 'P'}{product_id}-{color_name}-{size_label}",
                            'available': stock_value > 0
                        })

                    response_data['variants'].append(variant_data)

            except Exception as e:
                print(f"Error parsing variants JSON: {e}")
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error in get_product_variants: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@main.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    """Add item to cart with enhanced variant and stock validation"""
    from flask import session, request, jsonify
    from project.models import SellerProduct, ProductVariant, VariantSize, CartItem, db
    
    try:
        data = request.get_json()
        
        # Extract item data
        product_id = data.get('product_id')
        color = data.get('color')
        size = data.get('size')
        quantity = int(data.get('quantity', 1))
        variant_id = data.get('variant_id')  # New: variant_id for direct variant reference
        size_id = data.get('size_id')  # New: size_id for direct size reference
        incoming_sku = (data.get('sku') or '').strip() or None
        
        # Validate required fields
        if not product_id:
            return jsonify({'error': 'Product ID is required'}), 400
        
        # Enforce per-item max quantity
        if quantity < 1:
            return jsonify({'error': 'Quantity must be at least 1'}), 400

        if quantity > MAX_CART_ITEM_QUANTITY:
            return jsonify({
                'error': f'Maximum of {MAX_CART_ITEM_QUANTITY} units per variant is allowed in the cart',
                'max_quantity': MAX_CART_ITEM_QUANTITY
            }), 400

        # Get product information
        product = SellerProduct.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Stock validation and variant resolution
        available_stock = 0
        actual_variant_id = variant_id
        actual_size_id = size_id
        product_name = product.name
        product_price = float(product.price)
        seller_id = product.seller_id
        fallback_image = _resolve_image_source(
            product.primary_image,
            '/static/image/banner_1.png'
        )
        variant_image = fallback_image
        
        resolved_sku = _generate_cart_item_sku(product, color, size, incoming_sku)

        # Method 1: Use variant_id and size_id if provided (new structure)
        if variant_id and size_id:
            variant_size = VariantSize.query.filter_by(
                variant_id=variant_id,
                id=size_id
            ).first()

            if variant_size:
                available_stock = variant_size.stock_quantity
                color = ProductVariant.query.get(variant_id).variant_name if not color else color
                size = variant_size.size_label if not size else size

                # Get variant images if available
                variant = ProductVariant.query.get(variant_id)
                if variant and variant.images_json:
                    variant_image = _resolve_image_source(
                        variant.images_json,
                        product.primary_image,
                        fallback_image
                    )
        elif color and size:
            # Method 2: Use color and size to find variant (legacy support)
            try:
                variants_data = _parse_variants_structure(product.variants)
                color_variant = _find_variant_by_color(variants_data, color)

                if color_variant:
                    stock_info = _build_stock_map_from_variant(color_variant)
                    for size_label, stock_count in stock_info.items():
                        label_normalized = str(size_label).strip().lower()
                        if label_normalized == str(size).strip().lower():
                            try:
                                available_stock = int(stock_count)
                            except Exception:
                                available_stock = int(float(stock_count) if stock_count else 0)
                            break

                    images = _extract_variant_images(color_variant)
                    resolved_img = _resolve_image_source(
                        images,
                        product.primary_image,
                        fallback_image
                    )
                    if resolved_img:
                        variant_image = resolved_img
            except Exception as e:
                print(f"Error parsing variants JSON: {e}")
        else:
            return jsonify({'error': 'Color and size are required'}), 400

        if not variant_image:
            variant_image = fallback_image

        # Validate stock availability
        if available_stock < quantity:
            return jsonify({
                'error': 'Insufficient stock',
                'available_stock': available_stock,
                'requested_quantity': quantity
            }), 409
        
        # Determine user identification for cart persistence
        user_id = current_user.id if current_user.is_authenticated else None
        session_id = session.get('session_id') if not user_id else None
        
        # Ensure session ID exists for anonymous users
        if not user_id and not session_id:
            import uuid
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
        
        # Check if item already exists in cart (database)
        existing_cart_item = None
        if user_id:
            existing_cart_item = CartItem.query.filter_by(
                user_id=user_id,
                product_id=product_id,
                color=color,
                size=size
            ).first()
        elif session_id:
            existing_cart_item = CartItem.query.filter_by(
                session_id=session_id,
                product_id=product_id,
                color=color,
                size=size
            ).first()
        
        if existing_cart_item:
            # Check if total quantity would exceed stock
            if existing_cart_item.quantity >= MAX_CART_ITEM_QUANTITY:
                return jsonify({
                    'error': f'Maximum quantity of {MAX_CART_ITEM_QUANTITY} for this variant is already in your cart',
                    'max_quantity': MAX_CART_ITEM_QUANTITY
                }), 409

            total_quantity = existing_cart_item.quantity + quantity
            if total_quantity > MAX_CART_ITEM_QUANTITY:
                return jsonify({
                    'error': f'You can only keep up to {MAX_CART_ITEM_QUANTITY} of the same variant in your cart',
                    'max_quantity': MAX_CART_ITEM_QUANTITY,
                    'current_in_cart': existing_cart_item.quantity,
                    'requested_additional': quantity
                }), 409

            if total_quantity > available_stock:
                return jsonify({
                    'error': 'Total quantity would exceed available stock',
                    'available_stock': available_stock,
                    'current_in_cart': existing_cart_item.quantity,
                    'requested_additional': quantity
                }), 409
            
            # Update existing item
            existing_cart_item.quantity = total_quantity
            existing_cart_item.updated_at = datetime.utcnow()
            if variant_image and variant_image != existing_cart_item.variant_image:
                existing_cart_item.variant_image = variant_image
            db.session.commit()
            cart_item = existing_cart_item
        else:
            # Create new cart item
            cart_item = CartItem(
                user_id=user_id,
                session_id=session_id,
                product_id=product_id,
                product_name=product_name,
                product_price=product_price,
                color=color,
                size=size,
                quantity=quantity,
                variant_image=variant_image,
                seller_id=seller_id
            )
            db.session.add(cart_item)
            db.session.commit()
        
        # Update session cart for immediate UI feedback
        cart_items = session.get('cart_items', [])
        session_item = None
        for item in cart_items:
            if (item.get('product_id') == product_id and 
                item.get('color') == color and 
                item.get('size') == size):
                session_item = item
                break
        
        if session_item:
            session_item['quantity'] = cart_item.quantity
            session_item['max_quantity'] = MAX_CART_ITEM_QUANTITY
        else:
            cart_items.append({
                'id': cart_item.id,
                'product_id': product_id,
                'product_name': product_name,
                'product_price': product_price,
                'color': color,
                'size': size,
                'quantity': quantity,
                'variant_image': variant_image,
                'seller_id': seller_id,
                'added_at': datetime.now().isoformat(),
                'max_quantity': MAX_CART_ITEM_QUANTITY
            })
        
        session['cart_items'] = cart_items
        
        # Get total cart count (count distinct cart item rows, not sum of quantities)
        if user_id:
            total_count = db.session.query(db.func.count(CartItem.id)).filter_by(user_id=user_id).scalar() or 0
        else:
            total_count = db.session.query(db.func.count(CartItem.id)).filter_by(session_id=session_id).scalar() or 0
        
        # Build a stable item payload to return to the client. Ensure common keys exist
        if hasattr(cart_item, 'to_dict'):
            item_payload = cart_item.to_dict()
        else:
            item_payload = {
                'id': getattr(cart_item, 'id', None),
                'product_id': product_id,
                'product_name': product_name,
                'product_price': product_price,
                'color': color,
                'size': size,
                'quantity': getattr(cart_item, 'quantity', quantity),
                'variant_image': variant_image,
                'available_stock': available_stock
            }

        item_payload['sku'] = item_payload.get('sku') or resolved_sku

        # Normalize and ensure fields are present
        try:
            item_payload['product_name'] = item_payload.get('product_name') or product_name
            # Ensure numeric price
            item_payload['product_price'] = float(item_payload.get('product_price') or product_price or 0)
            item_payload['variant_image'] = item_payload.get('variant_image') or variant_image or _normalize_image_path(product.primary_image) or '/static/image/banner.png'
            item_payload['quantity'] = int(item_payload.get('quantity') or quantity or 1)
            item_payload['sku'] = item_payload.get('sku') or _generate_cart_item_sku(product, color, size, resolved_sku)
            item_payload['max_quantity'] = MAX_CART_ITEM_QUANTITY
        except Exception:
            # best-effort defaults
            item_payload.setdefault('product_name', product_name)
            item_payload.setdefault('product_price', float(product_price or 0))
            item_payload.setdefault('variant_image', variant_image or fallback_image)
            item_payload.setdefault('quantity', int(quantity or 1))
            item_payload.setdefault('sku', _generate_cart_item_sku(product, color, size, resolved_sku))
            item_payload.setdefault('max_quantity', MAX_CART_ITEM_QUANTITY)

        return jsonify({
            'success': True,
            'message': 'Item added to cart',
            'cart_count': int(total_count),
            'item': item_payload
        })
        
    except Exception as e:
        print(f"Error adding to cart: {e}")
        return jsonify({'error': 'Failed to add item to cart'}), 500


@main.route('/remove-from-cart', methods=['POST'])
def remove_from_cart():
    """Remove an item from the cart (DB + session) and return updated totals."""
    from flask import session, request, jsonify
    from project.models import CartItem

    try:
        data = request.get_json(force=True, silent=True) or request.form or {}
        item_id = data.get('item_id') or data.get('id')

        if not item_id:
            return jsonify({'error': 'Item id is required'}), 400

        user_id = current_user.id if current_user.is_authenticated else None
        session_id = session.get('session_id') if not user_id else None

        # Try to find the cart item in DB
        cart_item = None
        try:
            # allow numeric ids
            item_id_int = int(item_id)
        except Exception:
            item_id_int = None

        if item_id_int:
            if user_id:
                cart_item = CartItem.query.filter_by(id=item_id_int, user_id=user_id).first()
            elif session_id:
                cart_item = CartItem.query.filter_by(id=item_id_int, session_id=session_id).first()

        # If not found by id, try matching by composed id key used in session
        if not cart_item:
            # Remove from session store only if present
            pass

        # Remove DB row if exists
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()

        # Remove from session['cart_items'] if present
        session_items = session.get('cart_items', [])
        new_session_items = []
        removed = False
        for it in session_items:
            # match by id or by product/color/size composite
            if (str(it.get('id')) == str(item_id)) or (str(it.get('id')) == str(item_id_int)):
                removed = True
                continue
            # also allow matching by product/color/size composite id created earlier
            if isinstance(it.get('id'), str) and str(it.get('id')) == str(item_id):
                removed = True
                continue
            new_session_items.append(it)

        if removed:
            session['cart_items'] = new_session_items

        # Recompute cart summary values
        raw_items = []
        if current_user.is_authenticated:
            db_items = CartItem.query.filter_by(user_id=current_user.id).all()
            raw_items = [item.to_dict() for item in db_items]
        else:
            raw_items = session.get('cart_items', [])

        subtotal = 0
        total_count = 0
        for item in raw_items:
            try:
                price = float(item.get('product_price') or item.get('price') or 0)
                quantity = int(item.get('quantity') or 1)
                subtotal += price * quantity
                total_count += 1
            except Exception:
                continue

        return jsonify({'success': True, 'cart_count': int(total_count), 'subtotal': round(subtotal, 2)})
    except Exception as e:
        print(f"Error removing cart item: {e}")
        return jsonify({'error': 'Failed to remove item'}), 500


@main.route('/update-cart-quantity', methods=['POST'])
def update_cart_quantity():
    """Update the quantity of a cart item while enforcing limits."""
    from flask import session, request, jsonify
    from project.models import CartItem, SellerProduct

    try:
        data = request.get_json(force=True, silent=True) or request.form or {}
        item_id = data.get('item_id') or data.get('id')
        desired_quantity = data.get('quantity')

        if not item_id:
            return jsonify({'error': 'Item id is required'}), 400

        try:
            desired_quantity = int(desired_quantity)
        except Exception:
            return jsonify({'error': 'Quantity must be a number'}), 400

        if desired_quantity < 1:
            desired_quantity = 1
        if desired_quantity > MAX_CART_ITEM_QUANTITY:
            return jsonify({
                'error': f'Maximum of {MAX_CART_ITEM_QUANTITY} units per variant is allowed in the cart',
                'max_quantity': MAX_CART_ITEM_QUANTITY
            }), 400

        user_id = current_user.id if current_user.is_authenticated else None
        session_id = session.get('session_id') if not user_id else None

        cart_item = None
        try:
            item_id_int = int(item_id)
        except Exception:
            item_id_int = None

        if item_id_int:
            if user_id:
                cart_item = CartItem.query.filter_by(id=item_id_int, user_id=user_id).first()
            elif session_id:
                cart_item = CartItem.query.filter_by(id=item_id_int, session_id=session_id).first()

        if not cart_item:
            return jsonify({'error': 'Cart item not found'}), 404

        cart_item.quantity = desired_quantity
        cart_item.updated_at = datetime.utcnow()
        db.session.commit()

        # Update session cache
        session_items = session.get('cart_items', [])
        for it in session_items:
            if str(it.get('id')) == str(cart_item.id):
                it['quantity'] = desired_quantity
                it['max_quantity'] = MAX_CART_ITEM_QUANTITY
                break
        session['cart_items'] = session_items

        # Recompute summary data
        if user_id:
            db_items = CartItem.query.filter_by(user_id=user_id).all()
            raw_items = [item.to_dict() for item in db_items]
        else:
            raw_items = session.get('cart_items', [])

        subtotal = 0
        total_count = 0
        for item in raw_items:
            try:
                price = float(item.get('product_price') or item.get('price') or 0)
                quantity = int(item.get('quantity') or 1)
                subtotal += price * quantity
                total_count += 1
            except Exception:
                continue

        return jsonify({
            'success': True,
            'quantity': desired_quantity,
            'cart_count': int(total_count),
            'subtotal': round(subtotal, 2)
        })
    except Exception as e:
        print(f"Error updating cart quantity: {e}")
        return jsonify({'error': 'Failed to update quantity'}), 500


@main.route('/checkout')
@login_required
def buyer_checkout():
    """Display checkout page"""
    nav_items = get_nav_items()
    cart_items = []  # TODO: Fetch cart items from session/database
    
    # Calculate summary values
    subtotal = 0
    discount = 0
    delivery_fee = 0
    total = 0
    
    if cart_items:
        subtotal = sum(float(item.get('price', 0)) * int(item.get('quantity', 1)) for item in cart_items)
        discount = subtotal * 0.2  # 20% discount
        delivery_fee = 15
        total = subtotal - discount + delivery_fee
    
    return render_template(
        'main/checkout.html',
        nav_items=nav_items,
        cart_items=cart_items,
        subtotal=subtotal,
        discount=discount,
        delivery_fee=delivery_fee,
        total=total
    )

@main.route('/payment')
@login_required
def payment():
    """Display payment page"""
    nav_items = get_nav_items()
    cart_items = []  # TODO: Fetch cart items from session/database
    
    # Calculate summary values
    subtotal = 0
    discount = 0
    delivery_fee = 0
    total = 0
    
    if cart_items:
        subtotal = sum(float(item.get('price', 0)) * int(item.get('quantity', 1)) for item in cart_items)
        discount = subtotal * 0.2  # 20% discount
        delivery_fee = 15
        total = subtotal - discount + delivery_fee
    
    return render_template(
        'main/payment.html',
        nav_items=nav_items,
        user=current_user,
        cart_items=cart_items,
        subtotal=subtotal,
        discount=discount,
        delivery_fee=delivery_fee,
        total=total
    )

@main.route('/order-success')
@login_required
def order_success():
    """Show order confirmation message with quick actions"""
    nav_items = get_nav_items()

    cart_items = session.get('cart_items', []) or []
    subtotal = 0
    total_items = 0
    for item in cart_items:
        try:
            price = float(item.get('product_price') or item.get('price') or 0)
            qty = int(item.get('quantity') or 1)
        except Exception:
            price = 0
            qty = 1
        subtotal += price * qty
        total_items += qty

    delivery_fee = 0 if subtotal >= 1500 or subtotal == 0 else 150
    total = subtotal + delivery_fee

    order_number = session.get('latest_order_number')
    if not order_number:
        order_number = f"DIO-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        session['latest_order_number'] = order_number

    order_summary = {
        'order_number': order_number,
        'items_count': total_items,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'total': total,
        'estimated_delivery': session.get('latest_order_eta', '3-5 business days')
    }

    return render_template(
        'main/order_success.html',
        nav_items=nav_items,
        order_summary=order_summary
    )

@main.route('/my-purchases')
@login_required
def my_purchases():
    """Display buyer purchases grouped by order status with review deadlines"""
    nav_items = get_nav_items()
    selected_status = request.args.get('status') or 'pending'

    status_tabs = [
        {'id': 'pending', 'label': 'Pending'},
        {'id': 'shipping', 'label': 'Shipping'},
        {'id': 'in_transit', 'label': 'In Transit'},
        {'id': 'to_receive', 'label': 'To Be Received'},
        {'id': 'delivered', 'label': 'Delivered'},
        {'id': 'completed', 'label': 'Completed'},
    ]

    now = datetime.utcnow()
    sample_orders = [
        {
            'id': 'ORD-2024-3412',
            'placed_at': now - timedelta(days=1, hours=3),
            'status': 'pending',
            'status_message': 'Awaiting payment confirmation',
            'total': 1899.00,
            'items': [
                {
                    'id': 1,
                    'name': 'PopFlex - Pirouette Skort',
                    'variant': 'Cool White · L',
                    'price': 1899.00,
                    'quantity': 1,
                    'image': '/static/uploads/products/sample_skirt.png'
                }
            ],
            'timeline': {
                'next_action': 'Complete payment to proceed with shipping',
                'eta': None
            }
        },
        {
            'id': 'ORD-2024-3375',
            'placed_at': now - timedelta(days=3),
            'status': 'shipping',
            'status_message': 'Package is being prepared by the seller',
            'total': 2499.00,
            'items': [
                {
                    'id': 2,
                    'name': 'AeroCore Running Shoes',
                    'variant': 'Slate Gray · 42',
                    'price': 2499.00,
                    'quantity': 1,
                    'image': '/static/uploads/products/sample_shoes.png'
                }
            ],
            'timeline': {
                'next_action': 'Seller will hand this to the courier soon',
                'eta': (now + timedelta(days=2)).strftime('%b %d, %Y')
            }
        },
        {
            'id': 'ORD-2024-3321',
            'placed_at': now - timedelta(days=5),
            'status': 'in_transit',
            'status_message': 'Courier has picked up the parcel',
            'total': 1420.00,
            'tracking_number': 'JPX123456789',
            'items': [
                {
                    'id': 3,
                    'name': 'Zenlinen Relax Tee',
                    'variant': 'Moss Green · M',
                    'price': 710.00,
                    'quantity': 2,
                    'image': '/static/uploads/products/sample_top.png'
                }
            ],
            'timeline': {
                'next_action': 'Currently with courier – expect delivery soon',
                'eta': (now + timedelta(days=1)).strftime('%b %d, %Y')
            }
        },
        {
            'id': 'ORD-2024-3278',
            'placed_at': now - timedelta(days=7),
            'status': 'to_receive',
            'status_message': 'Out for delivery',
            'total': 985.00,
            'tracking_number': 'PHL556677889',
            'items': [
                {
                    'id': 4,
                    'name': 'CozyKnit Lounge Pants',
                    'variant': 'Charcoal · L',
                    'price': 985.00,
                    'quantity': 1,
                    'image': '/static/uploads/products/sample_pants.png'
                }
            ],
            'timeline': {
                'next_action': 'Please be available to receive your parcel',
                'eta': now.strftime('%b %d, %Y')
            }
        },
        {
            'id': 'ORD-2024-3204',
            'placed_at': now - timedelta(days=10),
            'status': 'delivered',
            'status_message': 'Delivered successfully',
            'delivered_at': now - timedelta(days=2),
            'review_deadline': (now - timedelta(days=2)) + timedelta(days=7),
            'total': 2050.00,
            'items': [
                {
                    'id': 5,
                    'name': 'Aurora Silk Dress',
                    'variant': 'Rose Dawn · S',
                    'price': 2050.00,
                    'quantity': 1,
                    'image': '/static/uploads/products/sample_dress.png',
                    'is_reviewed': False
                }
            ],
            'timeline': {
                'next_action': 'Write a review within 7 days',
                'eta': None
            }
        },
        {
            'id': 'ORD-2024-3011',
            'placed_at': now - timedelta(days=20),
            'status': 'completed',
            'status_message': 'Automatically completed after review window',
            'delivered_at': now - timedelta(days=12),
            'review_deadline': (now - timedelta(days=12)) + timedelta(days=7),
            'total': 1599.00,
            'items': [
                {
                    'id': 6,
                    'name': 'Lumina Wireless Earbuds',
                    'variant': 'Frost White',
                    'price': 1599.00,
                    'quantity': 1,
                    'image': '/static/uploads/products/sample_earbuds.png',
                    'is_reviewed': True,
                    'review': {
                        'rating': 5,
                        'title': 'Crystal clear sound',
                        'comment': 'Battery easily lasts my daily commute.'
                    }
                }
            ],
            'timeline': {
                'next_action': 'Order completed',
                'eta': None
            }
        }
    ]

    statuses_data = {tab['id']: {'orders': []} for tab in status_tabs}
    status_counts = {tab['id']: 0 for tab in status_tabs}

    for order in sample_orders:
        status_key = order['status']
        if status_key not in statuses_data:
            continue
        review_deadline = order.get('review_deadline')
        if review_deadline:
            remaining_days = (review_deadline - now).days
            order['review_days_left'] = max(0, remaining_days)
            order['auto_complete_on'] = review_deadline.strftime('%b %d, %Y')
            order['auto_completed'] = review_deadline < now and status_key == 'completed'
        statuses_data[status_key]['orders'].append(order)
        status_counts[status_key] += 1

    if selected_status not in statuses_data:
        selected_status = 'pending'

    return render_template(
        'main/my_purchases.html',
        nav_items=nav_items,
        status_tabs=status_tabs,
        statuses_data=statuses_data,
        status_counts=status_counts,
        selected_status=selected_status,
        now=now
    )

@main.route('/product/<product_id>')
def product_detail(product_id):
    """Display product detail page"""
    nav_items = get_nav_items()
    # Attempt to load product from SellerProduct first, then legacy Product
    variant_photos = {}
    stock_data = {}
    product = {}
    product_price = 0
    selected_quantity = 1
    seller_info = None
    
    # Fetch current logged-in user's seller information if they are a seller
    if current_user.is_authenticated and current_user.role == 'seller':
        try:
            if current_user.seller_profile:
                seller_profiles = current_user.seller_profile
                if seller_profiles:
                    seller_profile = seller_profiles[0]
                    
                    # Format joined date
                    joined_date = current_user.created_at.strftime('%B %Y') if current_user.created_at else 'Recently'
                    
                    # Format last active
                    last_active = 'Recently'
                    if seller_profile.last_active:
                        from datetime import datetime, timedelta
                        now = datetime.utcnow()
                        diff = now - seller_profile.last_active
                        if diff.days > 0:
                            last_active = f'{diff.days} days ago'
                        elif diff.seconds > 3600:
                            hours = diff.seconds // 3600
                            last_active = f'{hours} hours ago'
                        else:
                            minutes = diff.seconds // 60
                            last_active = f'{minutes} minutes ago' if minutes > 0 else 'Just now'
                    
                    seller_info = {
                        'id': current_user.id,
                        'business_name': seller_profile.business_name,
                        'business_address': seller_profile.business_address,
                        'business_city': seller_profile.business_city,
                        'business_country': seller_profile.business_country,
                        'store_description': seller_profile.store_description,
                        'is_verified': seller_profile.is_verified,
                        'rating': 4.5,  # TODO: Calculate from actual reviews
                        'rating_count': seller_profile.rating_count or 0,
                        'products_count': seller_profile.products_count or 0,
                        'followers_count': seller_profile.followers_count or 0,
                        'joined_date': joined_date,
                        'last_active': last_active,
                        'created_at': current_user.created_at
                    }
        except Exception as e:
            print(f"Error fetching current user's seller info: {e}")
            seller_info = None

    try:
        # Try SellerProduct (more detailed model)
        try:
            sp = SellerProduct.query.get(int(product_id))
        except Exception:
            sp = None

        if sp:
            # Fetch seller information
            try:
                seller_user = User.query.get(sp.seller_id)
                if seller_user and seller_user.seller_profile:
                    # seller_profile is a list due to backref, get the first one
                    seller_profiles = seller_user.seller_profile
                    if seller_profiles:
                        seller_profile = seller_profiles[0]
                        
                        # Calculate seller statistics
                        from sqlalchemy import func
                        
                        # Count products by this seller
                        products_count = SellerProduct.query.filter_by(
                            seller_id=seller_user.id, 
                            status='active'
                        ).count()
                        
                        # Calculate average rating (placeholder - implement when reviews are added)
                        avg_rating = 4.5  # TODO: Calculate from actual reviews
                        
                        # Get actual statistics from seller profile
                        rating_count = seller_profile.rating_count or 0
                        followers_count = seller_profile.followers_count or 0
                        products_count = seller_profile.products_count or 0
                        
                        # Format joined date
                        joined_date = seller_user.created_at.strftime('%B %Y') if seller_user.created_at else 'Recently'
                        
                        # Format last active
                        last_active = 'Recently'
                        if seller_profile.last_active:
                            from datetime import datetime, timedelta
                            now = datetime.utcnow()
                            diff = now - seller_profile.last_active
                            if diff.days > 0:
                                last_active = f'{diff.days} days ago'
                            elif diff.seconds > 3600:
                                hours = diff.seconds // 3600
                                last_active = f'{hours} hours ago'
                            else:
                                minutes = diff.seconds // 60
                                last_active = f'{minutes} minutes ago' if minutes > 0 else 'Just now'
                        
                        seller_info = {
                            'id': seller_user.id,
                            'business_name': seller_profile.business_name,
                            'business_address': seller_profile.business_address,
                            'business_city': seller_profile.business_city,
                            'business_country': seller_profile.business_country,
                            'store_description': seller_profile.store_description,
                            'is_verified': seller_profile.is_verified,
                            'rating': avg_rating,
                            'rating_count': rating_count,
                            'products_count': products_count,
                            'followers_count': followers_count,
                            'joined_date': joined_date,
                            'last_active': last_active,
                            'created_at': seller_user.created_at
                        }
            except Exception as e:
                print(f"Error fetching seller info: {e}")
                # Create minimal seller_info with available data
                seller_info = {
                    'id': sp.seller_id if sp else None,
                    'business_name': None,
                    'business_city': None,
                    'business_country': None,
                    'store_description': None,
                    'is_verified': False,
                    'rating': 0.0,
                    'rating_count': 0,
                    'products_count': 0,
                    'followers_count': 0,
                    'joined_date': 'Recently',
                    'last_active': 'Recently'
                }
            # Build variant_photos and stock_data from variants JSON
            try:
                # Parse variants if it's a string
                variants_data = sp.variants
                if isinstance(variants_data, str):
                    import json
                    try:
                        variants_data = json.loads(variants_data)
                    except (json.JSONDecodeError, TypeError):
                        variants_data = []
                
                if isinstance(variants_data, list):
                    # Convert list of variants to structured data
                    for variant in variants_data:
                        if isinstance(variant, dict):
                            color = variant.get('color', 'Unknown')
                            color_hex = variant.get('colorHex', '#000000')
                            
                            # Generate a default color hex if missing
                            if not color_hex or color_hex == '#000000':
                                # Generate a color based on the color name
                                color_hex = generate_color_from_name(color)
                            
                            # Initialize color in stock_data if not exists
                            if color not in stock_data:
                                stock_data[color] = {}
                            
                            # Handle both old and new variant structures
                            if 'sizeStocks' in variant:
                                # New structure: sizeStocks array
                                for size_item in variant['sizeStocks']:
                                    if isinstance(size_item, dict):
                                        size = size_item.get('size', 'OS')
                                        stock = size_item.get('stock', 0)
                                        stock_data[color][size] = stock
                            else:
                                # Old structure: single size and stock
                                size = variant.get('size') or 'One Size'
                                stock = variant.get('stock', 0)
                                stock_data[color][size] = stock
                            
                            # Set color hex for styling (store in variant_photos for now)
                            if color not in variant_photos:
                                variant_photos[color] = {
                                    'primary': sp.primary_image or '/static/image/banner.png',
                                    'secondary': sp.secondary_image or sp.primary_image or '/static/image/banner.png',
                                    'color_hex': color_hex
                                }
                elif isinstance(variants_data, dict):
                    # Handle existing dict structure
                    for color_key, v in variants_data.items():
                        if isinstance(v, dict):
                            imgs = v.get('images') or v.get('photos') or []
                            if imgs:
                                variant_photos[color_key] = {
                                    'primary': imgs[0],
                                    'secondary': imgs[1] if len(imgs) > 1 else None,
                                }
                            if isinstance(v.get('stock'), dict):
                                stock_data[color_key] = v.get('stock')
                        elif isinstance(v, list):
                            variant_photos[color_key] = {
                                'primary': v[0],
                                'secondary': v[1] if len(v) > 1 else None,
                            }
            except Exception:
                variant_photos = {}
                stock_data = {}

            primary = sp.primary_image or '/static/image/banner.png'
            secondary = sp.secondary_image or primary
            # Normalize size guides and certifications from attributes if present
            attrs = sp.attributes or {}
            raw_size_guides = attrs.get('size_guides') if isinstance(attrs, dict) else None
            raw_certifications = attrs.get('certifications') if isinstance(attrs, dict) else None
            def _normalize_list(paths):
                out = []
                if not paths:
                    return out
                try:
                    for p in paths:
                        if not p:
                            continue
                        s = str(p)
                        # Preserve data URIs and absolute URLs as-is
                        if s.startswith('data:') or s.startswith('http') or s.startswith('/'):
                            out.append(s)
                            continue
                        # Otherwise normalize local relative paths into /static/ URLs
                        url = _normalize_image_path(s)
                        if url:
                            out.append(url)
                except Exception:
                    pass
                return out

            size_guides = _normalize_list(raw_size_guides)
            certifications = _normalize_list(raw_certifications)

            product = {
                'id': sp.id,
                'name': sp.name,
                'description': sp.description or '',
                'price': float(sp.price or 0),
                'originalPrice': float(sp.compare_at_price) if sp.compare_at_price and sp.compare_at_price > sp.price else None,
                'primaryImage': primary,
                'secondaryImage': secondary,
                'materials': sp.materials,
                'details_fit': sp.details_fit,
                'variants': variants_data or {},
                'size_guides': size_guides,
                'certifications': certifications,
            }
            product_price = float(sp.price or 0)

        else:
            # Try legacy Product model
            try:
                p = Product.query.get(int(product_id))
            except Exception:
                p = None

            if p:
                product = p.to_public_dict()
                product.update({
                    'description': p.description or '',
                    'materials': p.materials,
                    'details_fit': getattr(p, 'details_fit', None),
                    'variants': {},
                })
                variant_photos = {}
                stock_data = {}
                product_price = float(p.price or 0)
                
                # For legacy products, try to get seller info if available
                if hasattr(p, 'seller_id') and p.seller_id:
                    try:
                        seller_user = User.query.get(p.seller_id)
                        if seller_user and seller_user.seller_profile:
                            seller_profiles = seller_user.seller_profile
                            if seller_profiles:
                                seller_profile = seller_profiles[0]
                                seller_info = {
                                    'id': seller_user.id,
                                    'business_name': seller_profile.business_name,
                                    'business_city': seller_profile.business_city,
                                    'business_country': seller_profile.business_country,
                                    'store_description': seller_profile.store_description,
                                    'is_verified': seller_profile.is_verified,
                                    'rating': 4.5,
                                    'rating_count': seller_profile.rating_count or 0,
                                    'products_count': seller_profile.products_count or 0,
                                    'followers_count': seller_profile.followers_count or 0,
                                    'joined_date': seller_user.created_at.strftime('%B %Y') if seller_user.created_at else 'Recently',
                                    'last_active': 'Recently'
                                }
                    except Exception as e:
                        print(f"Error fetching legacy seller info: {e}")
                        seller_info = None
            else:
                # Not found: keep product empty — template should handle missing data
                product = {
                    'id': product_id,
                    'name': 'Product not found',
                    'description': '',
                    'price': 0,
                    'primaryImage': '/static/image/banner.png',
                    'secondaryImage': '/static/image/banner.png',
                }
                seller_info = None

    except Exception:
        # Ensure we always return a usable template even on errors
        product = product or {}

    # Debug: Log the stock data being sent to template
    print("🔍 DEBUG: Final stock_data being sent to template:")
    for color, sizes in stock_data.items():
        print(f"  Color: {color}")
        for size, stock in sizes.items():
            print(f"    {size}: {stock} (type: {type(stock)})")

    return render_template(
        'main/product_detail.html',
        nav_items=nav_items,
        product=product,
        stock_data=stock_data,
        variant_photos=variant_photos,
        product_price=product_price,
        selected_quantity=selected_quantity,
        seller_info=seller_info,
    )


@main.route('/store/<int:seller_id>')
def store_page(seller_id):
    """Render a storefront page for the given seller ID."""
    nav_items = get_nav_items()
    
    try:
        # Fetch seller information
        seller_user = User.query.get(seller_id)
        if not seller_user or not seller_user.seller_profile:
            flash('Store not found', 'error')
            return redirect(url_for('main.index'))
        
        seller_profile = seller_user.seller_profile[0]
        
        # Get seller statistics from the seller profile
        products_count = seller_profile.products_count or 0
        followers_count = seller_profile.followers_count or 0
        rating_count = seller_profile.rating_count or 0
        
        # Calculate average rating from reviews if available
        avg_rating = 4.5  # Default rating
        if rating_count > 0:
            # TODO: Calculate actual average from ProductReviewNew table
            avg_rating = 4.5
        
        # Format joined date
        joined_date = seller_user.created_at.strftime('%B %Y') if seller_user.created_at else 'Recently'
        
        # Format location
        location_parts = []
        if seller_profile.business_city:
            location_parts.append(seller_profile.business_city)
        if seller_profile.business_country:
            location_parts.append(seller_profile.business_country)
        store_location = ', '.join(location_parts) if location_parts else 'Location not specified'
        
        def fmt_count(n):
            try:
                n = int(n)
            except Exception:
                return str(n)
            if n >= 1_000_000:
                v = round(n / 1_000_000, 1)
                return f"{v:g}M"
            if n >= 1000:
                v = round(n / 1000, 1)
                s = f"{v}K"
                if s.endswith('.0K'):
                    s = s.replace('.0K', 'K')
                return s
            return str(n)

        products_sold_display = fmt_count(products_count)
        followers_display = fmt_count(followers_count)

        return render_template(
            'main/store_page.html',
            nav_items=nav_items,
            store_name=seller_profile.business_name,
            store_location=store_location,
            products_sold_display=products_sold_display,
            followers_display=followers_display,
            products_sold=products_count,
            followers=followers_count,
            seller_info={
                'id': seller_user.id,
                'business_name': seller_profile.business_name,
                'business_address': seller_profile.business_address,
                'business_city': seller_profile.business_city,
                'business_country': seller_profile.business_country,
                'store_description': seller_profile.store_description,
                'is_verified': seller_profile.is_verified,
                'rating': avg_rating,
                'rating_count': rating_count,
                'products_count': products_count,
                'followers_count': followers_count,
                'total_sales': seller_profile.total_sales or 0,
                'joined_date': joined_date,
                'last_active': seller_profile.last_active
            }
        )
        
    except Exception as e:
        print(f"Error loading store page: {e}")
        flash('Error loading store page', 'error')
        return redirect(url_for('main.index'))

# Keep the old route for backward compatibility
@main.route('/store/<store_name>')
def store_page_by_name(store_name):
    """Legacy route for store pages by name - redirects to seller ID route"""
    # Try to find seller by business name
    try:
        seller_profile = Seller.query.filter_by(business_name=store_name.replace('-', ' ')).first()
        if seller_profile:
            return redirect(url_for('main.store_page', seller_id=seller_profile.user_id))
    except Exception:
        pass
    
    # Fallback to generic store page
    nav_items = get_nav_items()
    display_name = (store_name or 'Store').replace('-', ' ')
    store_location = 'Location not specified'

    return render_template(
        'main/store_page.html',
        nav_items=nav_items,
        store_name=display_name,
        store_location=store_location,
        products_sold_display='0',
        followers_display='0',
        products_sold=0,
        followers=0,
    )



@main.route('/health')
def health():
    """Health check endpoint"""
    try:
        # Test database connection
        user_count = User.query.count()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
        user_count = 0

    return jsonify({
        "status": "healthy",
        "database": db_status,
        "oauth": "configured",
        "users": user_count
    })

@main.route('/test-db')
def test_db():
    """Test database connectivity"""
    try:
        user_count = User.query.count()
        return jsonify({
            "database_status": "connected",
            "user_count": user_count,
            "message": "Database connection successful"
        })
    except Exception as e:
        return jsonify({
            "database_status": "error",
            "error": str(e),
            "message": "Database connection failed"
        }), 500


# ============================================
# CLOTHING ROUTES
# ============================================


# Helper: fetch products from SellerProduct or Product models and return
# a list of lightweight dicts compatible with the product card JS/template.
def fetch_products(category=None, subcategory=None, limit=48):
    results = []
    try:
        # Prefer SellerProduct (detailed seller table) when available
        q = SellerProduct.query.filter(SellerProduct.status == 'active')
        if category:
            q = q.filter(func.lower(SellerProduct.category) == category.lower())
        if subcategory:
            q = q.filter(func.lower(SellerProduct.subcategory) == subcategory.lower())
        q = q.order_by(SellerProduct.updated_at.desc()).limit(limit)
        seller_items = q.all()
        for s in seller_items:
            d = s.to_dict()
            # Normalize keys to match Product.to_public_dict shape used by frontend
            results.append({
                'id': d.get('id'),
                'name': d.get('name'),
                'price': d.get('price') or 0,
                'primaryImage': d.get('primary_image') or '/static/image/banner.png',
                'secondaryImage': getattr(s, 'secondary_image', None) or d.get('primary_image') or '/static/image/banner.png',
                'material': (getattr(s, 'materials', None) or 'Premium Material').split('\n')[0],
                'originalPrice': d.get('compare_at_price') or None,
            })

        # If no seller items found, fallback to Product model
        if not results:
            pq = Product.query.filter(func.lower(Product.status) == 'active')
            if category:
                pq = pq.filter(func.lower(Product.category) == category.lower())
            if subcategory:
                pq = pq.filter(func.lower(Product.subcategory) == subcategory.lower())
            pq = pq.order_by(Product.updated_at.desc()).limit(limit)
            for p in pq.all():
                pd = p.to_public_dict()
                results.append(pd)

    except Exception:
        # On error, return empty list (page will continue gracefully)
        return []

    return results

@main.route('/shop/all/clothing')
def shop_all_clothing():
    """Shop all clothing items"""
    nav_items = get_nav_items()
    products = fetch_products(category='clothing', limit=48)
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='clothing', selected_category='clothing')

@main.route('/shop/clothing/tops')
def shop_clothing_tops():
    """Shop clothing tops"""
    nav_items = get_nav_items()
    products = fetch_products(category='clothing', subcategory='tops', limit=48)
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='clothing', subcategory='tops', selected_category='clothing')

@main.route('/shop/clothing/bottoms')
def shop_clothing_bottoms():
    """Shop clothing bottoms"""
    nav_items = get_nav_items()
    products = fetch_products(category='clothing', subcategory='bottoms', limit=48)
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='clothing', subcategory='bottoms', selected_category='clothing')

@main.route('/shop/clothing/dresses')
def shop_clothing_dresses():
    """Shop dresses"""
    nav_items = get_nav_items()
    products = fetch_products(category='clothing', subcategory='dresses', limit=48)
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='clothing', subcategory='dresses', selected_category='clothing')

@main.route('/shop/clothing/outwear')
def shop_clothing_outwear():
    """Shop outerwear"""
    nav_items = get_nav_items()
    products = fetch_products(category='clothing', subcategory='outwear', limit=48)
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='clothing', subcategory='outwear', selected_category='clothing')

@main.route('/shop/clothing/activewear')
def shop_clothing_activewear():
    """Shop activewear"""
    nav_items = get_nav_items()
    products = fetch_products(category='clothing', subcategory='activewear', limit=48)
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='clothing', subcategory='activewear', selected_category='clothing')

@main.route('/shop/clothing/sleepwear')
def shop_clothing_sleepwear():
    """Shop sleepwear"""
    nav_items = get_nav_items()
    products = fetch_products(category='clothing', subcategory='sleepwear', limit=48)
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='clothing', subcategory='sleepwear', selected_category='clothing')

@main.route('/shop/clothing/undergarments')
def shop_clothing_undergarments():
    """Shop undergarments"""
    nav_items = get_nav_items()
    products = fetch_products(category='clothing', subcategory='undergarments', limit=48)
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='clothing', subcategory='undergarments', selected_category='clothing')

@main.route('/shop/clothing/swimwear')
def shop_clothing_swimwear():
    """Shop swimwear"""
    nav_items = get_nav_items()
    products = fetch_products(category='clothing', subcategory='swimwear', limit=48)
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='clothing', subcategory='swimwear', selected_category='clothing')

@main.route('/shop/clothing/occasionwear')
def shop_clothing_occasionwear():
    """Shop occasionwear"""
    nav_items = get_nav_items()
    products = fetch_products(category='clothing', subcategory='occasionwear', limit=48)
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='clothing', subcategory='occasionwear', selected_category='clothing')


# ============================================
# SHOES ROUTES
# ============================================

@main.route('/shop/all/shoes')
def shop_all_shoes():
    """Shop all shoes"""
    nav_items = get_nav_items()
    products = fetch_products(category='shoes', limit=48)
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='shoes', selected_category='shoes')

@main.route('/shop/shoes/heels')
def shop_shoes_heels():
    """Shop heels"""
    nav_items = get_nav_items()
    products = fetch_products(category='shoes', subcategory='heels', limit=48)
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='shoes', subcategory='heels', selected_category='shoes')

@main.route('/shop/shoes/flats')
def shop_shoes_flats():
    """Shop flats"""
    nav_items = get_nav_items()
    products = fetch_products(category='shoes', subcategory='flats', limit=48)
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='shoes', subcategory='flats', selected_category='shoes')

@main.route('/shop/shoes/sandals')
def shop_shoes_sandals():
    """Shop sandals"""
    nav_items = get_nav_items()
    products = fetch_products(category='shoes', subcategory='sandals', limit=48)
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='shoes', subcategory='sandals', selected_category='shoes')

@main.route('/shop/shoes/sneakers')
def shop_shoes_sneakers():
    """Shop sneakers"""
    nav_items = get_nav_items()
    products = fetch_products(category='shoes', subcategory='sneakers', limit=48)
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='shoes', subcategory='sneakers', selected_category='shoes')

@main.route('/shop/shoes/boots')
def shop_shoes_boots():
    """Shop boots"""
    nav_items = get_nav_items()
    products = fetch_products(category='shoes', subcategory='boots', limit=48)
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='shoes', subcategory='boots', selected_category='shoes')

@main.route('/shop/shoes/slippers')
def shop_shoes_slippers():
    """Shop slippers & comfort wear"""
    nav_items = get_nav_items()
    products = fetch_products(category='shoes', subcategory='slippers', limit=48)
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='shoes', subcategory='slippers', selected_category='shoes')

@main.route('/shop/shoes/occasion-shoes')
def shop_shoes_occasion_shoes():
    """Shop occasion/dress shoes"""
    nav_items = get_nav_items()
    products = fetch_products(category='shoes', subcategory='occasion-shoes', limit=48)
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='shoes', subcategory='occasion-shoes', selected_category='shoes')


# ============================================
# ACCESSORIES ROUTES
# ============================================

@main.route('/shop/all/accessories')
def shop_all_accessories():
    """Shop all accessories"""
    nav_items = get_nav_items()
    products = fetch_products(category='accessories', limit=48)
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='accessories', selected_category='accessories')

@main.route('/shop/accessories/bags')
def shop_accessories_bags():
    """Shop bags"""
    nav_items = get_nav_items()
    products = fetch_products(category='accessories', subcategory='bags', limit=48)
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='accessories', subcategory='bags', selected_category='accessories')

@main.route('/shop/accessories/jewelry')
def shop_accessories_jewelry():
    """Shop jewelry"""
    nav_items = get_nav_items()
    products = fetch_products(category='accessories', subcategory='jewelry', limit=48)
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='accessories', subcategory='jewelry', selected_category='accessories')

@main.route('/shop/accessories/hair-accessories')
def shop_accessories_hair_accessories():
    """Shop hair accessories"""
    nav_items = get_nav_items()
    products = fetch_products(category='accessories', subcategory='hair-accessories', limit=48)
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='accessories', subcategory='hair-accessories', selected_category='accessories')

@main.route('/shop/accessories/belts')
def shop_accessories_belts():
    """Shop belts"""
    nav_items = get_nav_items()
    products = fetch_products(category='accessories', subcategory='belts', limit=48)
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='accessories', subcategory='belts', selected_category='accessories')

@main.route('/shop/accessories/scarves-wraps')
def shop_accessories_scarves_wraps():
    """Shop scarves & wraps"""
    nav_items = get_nav_items()
    products = fetch_products(category='accessories', subcategory='scarves-wraps', limit=48)
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='accessories', subcategory='scarves-wraps', selected_category='accessories')

@main.route('/shop/accessories/hats-caps')
def shop_accessories_hats_caps():
    """Shop hats & caps"""
    nav_items = get_nav_items()
    products = fetch_products(category='accessories', subcategory='hats-caps', limit=48)
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='accessories', subcategory='hats-caps', selected_category='accessories')

@main.route('/shop/accessories/eyewear')
def shop_accessories_eyewear():
    """Shop eyewear"""
    nav_items = get_nav_items()
    products = fetch_products(category='accessories', subcategory='eyewear', limit=48)
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='accessories', subcategory='eyewear', selected_category='accessories')

@main.route('/shop/accessories/watches')
def shop_accessories_watches():
    """Shop watches"""
    nav_items = get_nav_items()
    products = fetch_products(category='accessories', subcategory='watches', limit=48)
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='accessories', subcategory='watches', selected_category='accessories')

@main.route('/shop/accessories/gloves')
def shop_accessories_gloves():
    """Shop gloves"""
    nav_items = get_nav_items()
    products = fetch_products(category='accessories', subcategory='gloves', limit=48)
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='accessories', subcategory='gloves', selected_category='accessories')

@main.route('/shop/accessories/others')
def shop_accessories_others():
    """Shop other accessories"""
    nav_items = get_nav_items()
    products = fetch_products(category='accessories', subcategory='others', limit=48)
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='accessories', subcategory='others', selected_category='accessories')


# Helper function to get navigation items
def get_nav_items():
    """Return navigation items for header"""
    return [
        {
            'name': 'Clothing',
            'bold': False,
            'active': False,
            'url': url_for('main.shop_all_clothing'),
            'dropdown': {
                'categories': ['Tops', 'Bottoms', 'Dresses', 'Outwear', 'Activewear', 'Sleepwear', 'Undergarments', 'Swimwear', 'Occasionwear'],
                'sections': [
                    {
                        'title': 'Women Tops',
                        'subitems': ['T-Shirts', 'Blouses', 'Button-downs', 'Tank Tops', 'Crop Tops', 'Tube Tops', 'Tunics', 'Wrap Tops', 'Peplum Tops', 'Bodysuits', 'Sweaters', 'Cardigans', 'Sweatshirts & Hoodies']
                    }
                ],
                'promo': {
                    'title': 'Spring Collection',
                    'subtitle': 'Fresh Styles Await',
                    'description': 'Discover the latest trends with our new spring collection.',
                    'button': 'Explore'
                }
            }
        },
        {
            'name': 'Shoes',
            'bold': False,
            'active': False,
            'url': url_for('main.shop_all_shoes'),
            'dropdown': {
                'categories': ['Heels', 'Flats', 'Sandals', 'Sneakers', 'Boots', 'Slippers & Comfort', 'Occasion Shoes'],
                'sections': [
                    {
                        'title': 'Heels',
                        'subitems': ['Stilettos', 'Pumps', 'Block Heels', 'Wedge Heels', 'Kitten Heels', 'Platform Heels', 'Ankle Strap Heels', 'Mules', 'Peep Toe Heels', 'Slingbacks']
                    }
                ],
                'promo': {
                    'title': 'Step Up',
                    'subtitle': 'New Shoe Collection',
                    'description': 'Walk in style with our curated shoe selection.',
                    'button': 'Shop Now'
                }
            }
        },
        {
            'name': 'Accessories',
            'bold': False,
            'active': False,
            'url': url_for('main.shop_all_accessories'),
            'dropdown': {
                'categories': ['Bags', 'Jewelry', 'Hair Accessories', 'Belts', 'Scarves & Wraps', 'Hats & Caps', 'Eyewear', 'Watches', 'Gloves', 'Others'],
                'sections': [
                    {
                        'title': 'Accessories',
                        'subitems': ['Handbags', 'Shoulder Bags', 'Tote Bags', 'Crossbody Bags', 'Clutches', 'Backpacks', 'Wallets & Pouches', 'Necklaces', 'Earrings', 'Bracelets']
                    }
                ],
                'promo': {
                    'title': 'Complete Your Look',
                    'subtitle': 'Accessory Essentials',
                    'description': 'Find the perfect finishing touch for any outfit.',
                    'button': 'Browse'
                }
            }
        },
        {
            'name': "What's New",
            'bold': True,
            'active': False,
            'dropdown': {
                'categories': ['New Arrivals', 'Best Sellers', 'Trending', 'Limited Edition', 'Seasonal'],
                'sections': [
                    {
                        'title': 'Latest Drops',
                        'subitems': ['This Week', 'This Month', 'Last 30 Days', 'Coming Soon']
                    }
                ],
                'promo': {
                    'title': 'Exclusive Launch',
                    'subtitle': 'Be First to Know',
                    'description': 'Get early access to our newest collections and exclusive drops.',
                    'button': 'Join Now'
                }
            }
        }
    ]

@main.route('/api/product/<int:product_id>/sizes/<color>')
def get_product_sizes_for_color(product_id, color):
    """Get available sizes for a specific product and color combination"""
    try:
        from project.models import ProductVariant, VariantSize
        
        # Try SellerProduct first
        product = SellerProduct.query.get(product_id)
        if not product:
            # Fallback to Product model
            product = Product.query.get(product_id)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        sizes_data = {}
        
        # First try ProductVariant and VariantSize tables
        variant = ProductVariant.query.filter_by(
            product_id=product_id,
            variant_name=color
        ).first()
        
        if variant:
            # Get all sizes for this color variant from database tables
            variant_sizes = VariantSize.query.filter_by(variant_id=variant.id).all()
            for vs in variant_sizes:
                sizes_data[vs.size_label] = {
                    'stock': vs.stock_quantity,
                    'available': vs.stock_quantity > 0
                }
        else:
            # Fallback to variants JSON structure
            try:
                variants_data = _parse_variants_structure(product.variants)
                color_variant = _find_variant_by_color(variants_data, color)

                if color_variant:
                    stock_info = _build_stock_map_from_variant(color_variant)
                    if stock_info:
                        for size_name, stock_qty in stock_info.items():
                            try:
                                stock_value = int(stock_qty)
                            except Exception:
                                stock_value = int(float(stock_qty) if stock_qty else 0)

                            sizes_data[size_name] = {
                                'stock': stock_value,
                                'available': stock_value > 0
                            }
                    else:
                        # Single-size schema fallback
                        size_name = color_variant.get('size', 'One Size')
                        try:
                            stock_value = int(color_variant.get('stock', 0))
                        except Exception:
                            stock_value = int(float(color_variant.get('stock', 0)) or 0)
                        sizes_data[size_name] = {
                            'stock': stock_value,
                            'available': stock_value > 0
                        }

            except Exception as e:
                print(f"Error parsing variants JSON: {e}")
        
        return jsonify({
            'success': True,
            'color': color,
            'sizes': sizes_data
        })
        
    except Exception as e:
        print(f"Error getting sizes for color: {e}")
        return jsonify({'error': 'Failed to get sizes'}), 500