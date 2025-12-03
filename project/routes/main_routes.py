"""
Main routes for Dione Ecommerce
"""
from flask import Blueprint, render_template, jsonify, redirect, url_for, flash, current_app, session
from flask import request
from flask_login import login_required, current_user, logout_user
from project import db
from project.models import Product, User, SellerProduct, ProductReport, Seller, CartItem, Order, OrderItem, Buyer

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


def fetch_products(category=None, subcategory=None, limit=48, seller_id=None):
    """Return a list of product dicts for a category/subcategory.

    This tries `SellerProduct` (the richer seller product table) first and
    falls back to the simpler `Product` table to fill up the requested limit.
    The returned items are lightweight dicts suitable for passing to templates
    and JS.
    """
    items = []
    try:
        q = SellerProduct.query.filter_by(is_draft=False)
        if category:
            q = q.filter(SellerProduct.category == category)
        if subcategory:
            q = q.filter(SellerProduct.subcategory == subcategory)
        if seller_id:
            q = q.filter(SellerProduct.seller_id == seller_id)
        seller_products = q.order_by(SellerProduct.created_at.desc()).limit(limit).all()
        for p in seller_products:
            try:
                items.append(p.to_dict())
            except Exception:
                # Best-effort: build a minimal dict
                items.append({
                    'id': getattr(p, 'id', None),
                    'name': getattr(p, 'name', None),
                    'primaryImage': _normalize_image_path(getattr(p, 'primary_image', None)) or '/static/image/banner.png',
                    'price': float(getattr(p, 'price', 0) or 0),
                    'category': getattr(p, 'category', None),
                    'subcategory': getattr(p, 'subcategory', None),
                })
    except Exception as e:
        print(f"Warning: fetch_products seller query failed: {e}")

    if len(items) < limit:
        remaining = limit - len(items)
        try:
            q2 = Product.query.filter(Product.status == 'active')
            if category:
                q2 = q2.filter(Product.category == category)
            if subcategory:
                q2 = q2.filter(Product.subcategory == subcategory)
            prods = q2.order_by(Product.created_at.desc()).limit(remaining).all()
            for p in prods:
                try:
                    items.append(p.to_public_dict())
                except Exception:
                    items.append({
                        'id': getattr(p, 'id', None),
                        'name': getattr(p, 'name', None),
                        'primaryImage': _normalize_image_path(getattr(p, 'image', None)) or '/static/image/banner.png',
                        'price': float(getattr(p, 'price', 0) or 0),
                        'category': getattr(p, 'category', None),
                        'subcategory': getattr(p, 'subcategory', None),
                    })
        except Exception as e:
            print(f"Warning: fetch_products product query failed: {e}")

    return items[:limit]


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
        # Extract colors from variants for frontend display
        colors = []
        variants = []
        
        try:
            # Parse variants JSON to extract colors
            variants_data = _parse_variants_structure(sp.variants)
            if variants_data:
                if isinstance(variants_data, list):
                    for variant in variants_data:
                        if isinstance(variant, dict):
                            color = variant.get('color')
                            if color and color not in colors:
                                colors.append(color)
                                # Use variant-specific image if available, otherwise fallback to product images
                                variant_image = _normalize_image_path(variant.get('photo')) or _normalize_image_path(sp.primary_image) or '/static/image/banner_1.png'
                                variants.append({
                                    'color': color,
                                    'colorHex': variant.get('colorHex', '#000000'),
                                    'image': variant_image,
                                    'secondaryImage': _normalize_image_path(sp.secondary_image) or variant_image
                                })
                elif isinstance(variants_data, dict):
                    for color_name, variant_info in variants_data.items():
                        if color_name not in colors:
                            colors.append(color_name)
                            # Extract image from variant info if available
                            variant_image = _normalize_image_path(sp.primary_image) or '/static/image/banner_1.png'
                            if isinstance(variant_info, dict):
                                variant_image = _normalize_image_path(variant_info.get('photo') or variant_info.get('image')) or variant_image
                            variants.append({
                                'color': color_name,
                                'colorHex': variant_info.get('colorHex', '#000000') if isinstance(variant_info, dict) else '#000000',
                                'image': variant_image,
                                'secondaryImage': _normalize_image_path(sp.secondary_image) or variant_image
                            })
        except Exception as e:
            print(f"Error parsing variants for product {sp.id}: {e}")
        
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
            'colors': colors,
            'variants': variants,
            'sellerId': sp.seller_id,
        }

    # Add empty variants to legacy products for consistency
    def add_empty_variants(product_dict):
        if 'colors' not in product_dict:
            product_dict['colors'] = []
        if 'variants' not in product_dict:
            product_dict['variants'] = []
        return product_dict

    product_buckets = {
        'featured': [add_empty_variants(product.to_public_dict()) for product in featured] + [seller_to_public_dict(sp) for sp in seller_featured],
        'trending': [add_empty_variants(product.to_public_dict()) for product in trending] + [seller_to_public_dict(sp) for sp in seller_trending],
        'new_arrivals': [add_empty_variants(product.to_public_dict()) for product in new_arrivals] + [seller_to_public_dict(sp) for sp in seller_new_arrivals],
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
        
        # Calculate sold count from order_items
        sold_count = db.session.query(func.sum(OrderItem.quantity)).filter(
            OrderItem.product_id == p.id,
            OrderItem.order_id.in_(
                db.session.query(Order.id).filter(Order.status.in_(['delivered', 'completed']))
            )
        ).scalar() or 0
        pd['soldCount'] = int(sold_count)
        
        # Add empty variants for legacy products
        pd['variants'] = []
        pd['colors'] = []
        
        items.append(pd)
    
    for sp in seller_products:
        # Extract colors from variants for frontend display
        colors = []
        variants = []
        
        try:
            # Parse variants JSON to extract colors
            variants_data = _parse_variants_structure(sp.variants)
            if variants_data:
                if isinstance(variants_data, list):
                    for variant in variants_data:
                        if isinstance(variant, dict):
                            color = variant.get('color')
                            if color and color not in colors:
                                colors.append(color)
                                # Use variant-specific image if available, otherwise fallback to product images
                                variant_image = _normalize_image_path(variant.get('photo')) or _normalize_image_path(sp.primary_image) or '/static/image/banner_1.png'
                                variants.append({
                                    'color': color,
                                    'colorHex': variant.get('colorHex', '#000000'),
                                    'image': variant_image,
                                    'secondaryImage': _normalize_image_path(sp.secondary_image) or variant_image
                                })
                elif isinstance(variants_data, dict):
                    for color_name, variant_info in variants_data.items():
                        if color_name not in colors:
                            colors.append(color_name)
                            # Extract image from variant info if available
                            variant_image = _normalize_image_path(sp.primary_image) or '/static/image/banner_1.png'
                            if isinstance(variant_info, dict):
                                variant_image = _normalize_image_path(variant_info.get('photo') or variant_info.get('image')) or variant_image
                            variants.append({
                                'color': color_name,
                                'colorHex': variant_info.get('colorHex', '#000000') if isinstance(variant_info, dict) else '#000000',
                                'image': variant_image,
                                'secondaryImage': _normalize_image_path(sp.secondary_image) or variant_image
                            })
        except Exception as e:
            print(f"Error parsing variants for product {sp.id}: {e}")
        
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
            'colors': colors,
            'variants': variants,
            'sellerId': sp.seller_id,
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
        variant = None
        try:
            variant = ProductVariant.query.filter_by(
                product_id=product_id,
                variant_name=color_name
            ).first()
        except Exception as e:
            # Possible schema mismatch between models and DB (older deployments).
            # Fall back to legacy JSON structure below.
            print(f"Warning: ProductVariant query failed, falling back to JSON: {e}")

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
        import traceback
        traceback.print_exc()
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
        
        # Check if product is available (use status instead of is_active)
        if hasattr(product, 'status') and product.status not in ['active', 'published']:
            return jsonify({'error': 'Product is not available'}), 404
        
        # Stock validation and variant resolution
        available_stock = 0
        actual_variant_id = variant_id
        actual_size_id = size_id
        product_name = getattr(product, 'name', None) or ''
        # Defensive conversion: product.price may be None or an unexpected type
        try:
            product_price = float(getattr(product, 'price', 0) or 0)
        except Exception:
            try:
                # Try converting from string if necessary
                product_price = float(str(getattr(product, 'price', 0) or 0))
            except Exception:
                product_price = 0.0
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
            # Create new cart item - seller_id FK constraint removed, so this should always work
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
            
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                # If there's still a user_id foreign key issue, try as guest user
                if user_id:
                    cart_item.user_id = None
                    cart_item.session_id = session.get('session_id', session_id or f"guest_{datetime.now().timestamp()}")
                    db.session.add(cart_item)
                    try:
                        db.session.commit()
                    except Exception:
                        db.session.rollback()
                        raise e  # Re-raise original error
                else:
                    raise e
        
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
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to add item to cart',
            'details': str(e),
            'success': False
        }), 500


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
    from datetime import datetime

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
            return jsonify({'error': 'Invalid item ID'}), 400

        if user_id:
            cart_item = CartItem.query.filter_by(id=item_id_int, user_id=user_id).first()
        elif session_id:
            cart_item = CartItem.query.filter_by(id=item_id_int, session_id=session_id).first()

        if not cart_item:
            return jsonify({'error': 'Cart item not found'}), 404

        # Update cart item quantity
        cart_item.quantity = desired_quantity
        cart_item.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Database error updating cart quantity: {e}")
            return jsonify({'error': 'Database error occurred'}), 500

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
                total_count += quantity
            except Exception:
                continue

        return jsonify({
            'success': True,
            'quantity': desired_quantity,
            'cart_count': int(total_count),
            'subtotal': round(subtotal, 2),
            'message': 'Quantity updated successfully'
        })
    except Exception as e:
        print(f"Error updating cart quantity: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update quantity'}), 500


@main.route('/set-checkout-items', methods=['POST'])
@login_required
def set_checkout_items():
    """Set selected cart items for checkout"""
    try:
        data = request.get_json()
        selected_item_ids = data.get('selected_item_ids', [])
        
        # Store selected item IDs in session
        session['selected_cart_items'] = selected_item_ids
        
        return jsonify({'success': True, 'message': 'Checkout items set successfully'})
    except Exception as e:
        print(f'Error setting checkout items: {e}')
        return jsonify({'error': 'Failed to set checkout items'}), 500

@main.route('/checkout')
@login_required
def buyer_checkout():
    """Display checkout page with user's shipping address and cart items"""
    nav_items = get_nav_items()
    
    # Fetch user's comprehensive shipping address from Buyer profile
    user_address = None
    buyer_profile = Buyer.query.filter_by(user_id=current_user.id).first()
    if buyer_profile:
        # Parse additional address data from JSON
        additional_data = {}
        try:
            import json
            if buyer_profile.preferred_language:
                additional_data = json.loads(buyer_profile.preferred_language)
        except (json.JSONDecodeError, TypeError):
            # If parsing fails, initialize empty data
            additional_data = {}
        
        user_address = {
            'first_name': additional_data.get('first_name', current_user.username or ''),
            'last_name': additional_data.get('last_name', ''),
            'address': buyer_profile.address or '',
            'apartment': additional_data.get('apartment', ''),
            'region': additional_data.get('region', ''),
            'state': additional_data.get('state', ''),
            'city': buyer_profile.city or '',
            'barangay': additional_data.get('barangay', ''),
            'zip_code': buyer_profile.zip_code or '',
            'phone': buyer_profile.phone or '',
            'country': buyer_profile.country or 'Philippines'
        }
    
    # Fetch cart items for the current user (only selected for checkout)
    cart_items = []
    cart_db_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    # Get selected item IDs from session storage (passed from cart page)
    selected_item_ids = session.get('selected_cart_items', [])
    
    subtotal = 0
    for item in cart_db_items:
        # Only include items that are selected for checkout
        if not selected_item_ids or item.id in selected_item_ids:
            cart_item = {
                'id': item.id,
                'name': item.product_name,
                'price': float(item.product_price or 0),
                'quantity': int(item.quantity or 1),
                'size': item.size,
                'color': item.color,
                'image_url': item.variant_image or item.product_image,
                'store_name': 'Dione Store',
                'selected_for_checkout': True
            }
            cart_items.append(cart_item)
            subtotal += cart_item['price'] * cart_item['quantity']
    
    # Calculate fees in PHP peso
    discount = 0  # No discount for now
    delivery_fee = 150 if subtotal < 1500 else 0  # Free shipping over ₱1500
    total = subtotal - discount + delivery_fee
    
    return render_template(
        'main/checkout.html',
        nav_items=nav_items,
        cart_items=cart_items,
        user_address=user_address,
        subtotal=subtotal,
        discount=discount,
        delivery_fee=delivery_fee,
        total=total
    )

@main.route('/update-address', methods=['POST'])
@login_required
def update_address():
    """Update user's shipping address with comprehensive data"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get or create buyer profile
        buyer_profile = Buyer.query.filter_by(user_id=current_user.id).first()
        if not buyer_profile:
            buyer_profile = Buyer(user_id=current_user.id)
            db.session.add(buyer_profile)
        
        # Update buyer profile with comprehensive address data
        buyer_profile.phone = data.get('phone', '')
        buyer_profile.address = data.get('address', '')
        buyer_profile.city = data.get('city', '')
        buyer_profile.zip_code = data.get('zipCode', '')
        buyer_profile.country = data.get('country', '')
        
        # Store region, province, and barangay in preferred_language field as JSON for now
        # In production, you would add proper fields to the database schema
        additional_address_data = {
            'region': data.get('region', ''),
            'state': data.get('state', ''),  # state = province
            'barangay': data.get('barangay', ''),
            'first_name': data.get('firstName', ''),
            'last_name': data.get('lastName', ''),
            'apartment': data.get('apartment', '')
        }
        
        # Store additional data as JSON string (temporary solution)
        import json
        buyer_profile.preferred_language = json.dumps(additional_address_data)
        
        # Update username if first name is provided
        if data.get('firstName'):
            current_user.username = data.get('firstName')
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Address updated successfully'})
    
    except Exception as e:
        print(f'Error updating address: {e}')
        db.session.rollback()
        return jsonify({'error': 'Failed to update address'}), 500

@main.route('/lookup-address/<zipcode>')
def lookup_address(zipcode):
    """Lookup Philippines address by ZIP code with comprehensive data"""
    try:
        # Comprehensive Philippines ZIP code database with region, province, city, and barangay
        zip_database = {
            '1000': {'region': 'National Capital Region (NCR)', 'province': 'Metro Manila', 'city': 'Manila', 'barangay': 'Malate'},
            '1001': {'region': 'National Capital Region (NCR)', 'province': 'Metro Manila', 'city': 'Manila', 'barangay': 'Intramuros'},
            '1002': {'region': 'National Capital Region (NCR)', 'province': 'Metro Manila', 'city': 'Manila', 'barangay': 'Binondo'},
            '1003': {'region': 'National Capital Region (NCR)', 'province': 'Metro Manila', 'city': 'Manila', 'barangay': 'Santa Cruz'},
            '1004': {'region': 'National Capital Region (NCR)', 'province': 'Metro Manila', 'city': 'Manila', 'barangay': 'Quiapo'},
            '1005': {'region': 'National Capital Region (NCR)', 'province': 'Metro Manila', 'city': 'Manila', 'barangay': 'San Nicolas'},
            '1100': {'region': 'National Capital Region (NCR)', 'province': 'Metro Manila', 'city': 'Quezon City', 'barangay': 'Diliman'},
            '1101': {'region': 'National Capital Region (NCR)', 'province': 'Metro Manila', 'city': 'Quezon City', 'barangay': 'Kamuning'},
            '1102': {'region': 'National Capital Region (NCR)', 'province': 'Metro Manila', 'city': 'Quezon City', 'barangay': 'Sacred Heart'},
            '1103': {'region': 'National Capital Region (NCR)', 'province': 'Metro Manila', 'city': 'Quezon City', 'barangay': 'Laging Handa'},
            '1104': {'region': 'National Capital Region (NCR)', 'province': 'Metro Manila', 'city': 'Quezon City', 'barangay': 'Bagong Silangan'},
            '1105': {'region': 'National Capital Region (NCR)', 'province': 'Metro Manila', 'city': 'Quezon City', 'barangay': 'Novaliches'},
            '1106': {'region': 'National Capital Region (NCR)', 'province': 'Metro Manila', 'city': 'Quezon City', 'barangay': 'Fairview'},
            '1200': {'region': 'National Capital Region (NCR)', 'province': 'Metro Manila', 'city': 'Makati', 'barangay': 'Poblacion'},
            '1201': {'region': 'National Capital Region (NCR)', 'province': 'Metro Manila', 'city': 'Makati', 'barangay': 'Legazpi Village'},
            '1202': {'region': 'National Capital Region (NCR)', 'province': 'Metro Manila', 'city': 'Makati', 'barangay': 'San Lorenzo'},
            '1203': {'region': 'National Capital Region (NCR)', 'province': 'Metro Manila', 'city': 'Makati', 'barangay': 'Bel-Air'},
            '1300': {'region': 'National Capital Region (NCR)', 'province': 'Metro Manila', 'city': 'Pasay', 'barangay': 'Malibay'},
            '1400': {'region': 'National Capital Region (NCR)', 'province': 'Metro Manila', 'city': 'Caloocan', 'barangay': 'Bagong Barrio'},
            '1500': {'region': 'National Capital Region (NCR)', 'province': 'Metro Manila', 'city': 'Taguig', 'barangay': 'Bonifacio Global City'},
            '1600': {'region': 'National Capital Region (NCR)', 'province': 'Metro Manila', 'city': 'Pasig', 'barangay': 'San Antonio'},
            '1700': {'region': 'National Capital Region (NCR)', 'province': 'Metro Manila', 'city': 'Parañaque', 'barangay': 'Baclaran'},
            '1800': {'region': 'National Capital Region (NCR)', 'province': 'Metro Manila', 'city': 'Marikina', 'barangay': 'Parang'},
            '4000': {'region': 'CALABARZON (Region IV-A)', 'province': 'Laguna', 'city': 'San Pablo', 'barangay': 'Poblacion'},
            '4100': {'region': 'CALABARZON (Region IV-A)', 'province': 'Rizal', 'city': 'Antipolo', 'barangay': 'Beverly Hills'},
            '4200': {'region': 'CALABARZON (Region IV-A)', 'province': 'Batangas', 'city': 'Batangas City', 'barangay': 'Poblacion'},
            '4300': {'region': 'CALABARZON (Region IV-A)', 'province': 'Quezon', 'city': 'Lucena', 'barangay': 'Dalahican'},
            '4400': {'region': 'Bicol Region (Region V)', 'province': 'Camarines Sur', 'city': 'Naga', 'barangay': 'Poblacion'},
            '4500': {'region': 'Bicol Region (Region V)', 'province': 'Albay', 'city': 'Legazpi', 'barangay': 'Bagong Abre'},
            '5000': {'region': 'Bicol Region (Region V)', 'province': 'Albay', 'city': 'Legaspi', 'barangay': 'Albay District'},
            '6000': {'region': 'Western Visayas (Region VI)', 'province': 'Iloilo', 'city': 'Iloilo City', 'barangay': 'City Proper'},
            '7000': {'region': 'Central Visayas (Region VII)', 'province': 'Cebu', 'city': 'Cebu City', 'barangay': 'Lahug'},
            '8000': {'region': 'Davao Region (Region XI)', 'province': 'Davao del Sur', 'city': 'Davao City', 'barangay': 'Poblacion District'},
            '9000': {'region': 'Northern Mindanao (Region X)', 'province': 'Misamis Oriental', 'city': 'Cagayan de Oro', 'barangay': 'Nazareth'},
            '2600': {'region': 'Cordillera Administrative Region (CAR)', 'province': 'Benguet', 'city': 'Baguio', 'barangay': 'Burnham-Legarda'}
        }
        
        address_data = zip_database.get(zipcode)
        
        if address_data:
            return jsonify({'success': True, 'data': address_data})
        else:
            return jsonify({'success': False, 'message': 'ZIP code not found'}), 404
            
    except Exception as e:
        print(f'Error looking up address: {e}')
        return jsonify({'error': 'Failed to lookup address'}), 500

@main.route('/philippines-address-api')
def philippines_address_api():
    """Comprehensive Philippines address API for dropdowns"""
    try:
        # Comprehensive Philippines address data
        philippines_data = {
            'regions': {
                'NCR': {
                    'name': 'National Capital Region (NCR)',
                    'provinces': {
                        'Metro Manila': {
                            'cities': {
                                'Manila': ['Binondo', 'Ermita', 'Intramuros', 'Malate', 'Paco', 'Pandacan', 'Port Area', 'Quiapo', 'Sampaloc', 'San Andres', 'San Miguel', 'San Nicolas', 'Santa Ana', 'Santa Cruz', 'Tondo'],
                                'Quezon City': ['Bagong Pag-asa', 'Bagong Silangan', 'Bago Bantay', 'Batasan Hills', 'Commonwealth', 'Cubao', 'Diliman', 'Fairview', 'Kamuning', 'La Loma', 'Libis', 'Novaliches', 'Project 4', 'Project 6', 'Sacred Heart', 'Tandang Sora'],
                                'Makati': ['Bel-Air', 'Cembo', 'Comembo', 'Dasmarinas', 'East Rembo', 'Forbes Park', 'Guadalupe Nuevo', 'Guadalupe Viejo', 'Kasilawan', 'La Paz', 'Legazpi Village', 'Magallanes', 'Olympia', 'Palanan', 'Pembo', 'Pinagkaisahan', 'Pio del Pilar', 'Poblacion', 'Rizal', 'San Antonio', 'San Isidro', 'San Lorenzo', 'Santa Cruz', 'Singkamas', 'South Cembo', 'Tejeros', 'Urdaneta', 'Valenzuela', 'West Rembo'],
                                'Pasig': ['Bagong Ilog', 'Bagong Katipunan', 'Bambang', 'Buting', 'Caniogan', 'Dela Paz', 'Kalawaan', 'Kapasigan', 'Kapitolyo', 'Malinao', 'Manggahan', 'Maybunga', 'Oranbo', 'Palatiw', 'Pinagbuhatan', 'Pineda', 'Rosario', 'Sagad', 'San Antonio', 'San Joaquin', 'San Jose', 'San Miguel', 'San Nicolas', 'Santa Lucia', 'Santa Rosa', 'Santo Tomas', 'Santolan', 'Sumilang', 'Ugong', 'Wawa'],
                                'Caloocan': ['Bagong Silang', 'Bagumbayan North', 'Bagumbayan South', 'Banlic', 'Barangka', 'Bonifacio', 'Buena Park', 'Caybiga', 'Deparo', 'Grace Park East', 'Grace Park West', 'Libjo', 'Letre', 'Maypajo', 'Morning Breeze', 'Poblacion', 'Tala', 'Tandang Sora'],
                                'Pasay': ['Baclaran', 'Maricaban', 'Malibay', 'San Isidro', 'San Rafael', 'Santa Clara', 'Santo Niño', 'Tripa de Gallina', 'Villamor'],
                                'Taguig': ['Bagumbayan', 'Bambang', 'Bayanan', 'Bicutan', 'Central Bicutan', 'Central Signal Village', 'Fort Bonifacio', 'Hagonoy', 'Ibayo-Tipas', 'Ligid-Tipas', 'Lower Bicutan', 'Maharlika Village', 'Napindan', 'New Lower Bicutan', 'North Daang Hari', 'North Signal Village', 'Palingon', 'Pinagsama', 'San Miguel', 'Santa Ana', 'South Daang Hari', 'South Signal Village', 'Tuktukan', 'Upper Bicutan', 'Ususan', 'Wawa', 'Western Bicutan'],
                                'Parañaque': ['B.F. Homes', 'Baclaran', 'Don Bosco', 'Don Galo', 'La Huerta', 'Marcelo Green', 'Merville', 'Moonwalk', 'San Antonio', 'San Dionisio', 'San Isidro', 'San Martin de Porres', 'Santo Niño', 'Sun Valley', 'Tambo', 'Vitalez'],
                                'Las Piñas': ['Almanza Dos', 'Almanza Uno', 'B.F. International Village', 'Daniel Fajardo', 'Elias Aldana', 'Ilaya', 'Manuyo Dos', 'Manuyo Uno', 'Pamplona Dos', 'Pamplona Tres', 'Pamplona Uno', 'Pilar', 'Pulang Lupa Dos', 'Pulang Lupa Uno', 'Talon Dos', 'Talon Kuatro', 'Talon Singko', 'Talon Tres', 'Talon Uno', 'Zapote'],
                                'Muntinlupa': ['Alabang', 'Bayanan', 'Buli', 'Cupang', 'Poblacion', 'Putatan', 'Sucat', 'Tunasan'],
                                'Marikina': ['Barangka', 'Calumpang', 'Concepcion Dos', 'Concepcion Uno', 'Fortune', 'Industrial Valley Complex', 'Jesus de la Peña', 'Malanday', 'Marikina Heights', 'Nangka', 'Parang', 'San Roque', 'Santa Elena', 'Santo Niño', 'Tañong', 'Tumana'],
                                'Valenzuela': ['Arkong Bato', 'Bagbaguin', 'Bignay', 'Bisig', 'Canumay East', 'Canumay West', 'Coloong', 'Dalandanan', 'Gen. T. de Leon', 'Hen. T. de Leon', 'Isla', 'Karuhatan', 'Lawang Bato', 'Lingunan', 'Mabolo', 'Malanday', 'Malinta', 'Mapulang Lupa', 'Marulas', 'Maysan', 'Palasan', 'Parada', 'Pariancillo Villa', 'Paso de Blas', 'Pasolo', 'Poblacion', 'Polo', 'Punturin', 'Rincon', 'Tagalag', 'Ugong', 'Viente Reales', 'Wawang Pulo']
                            }
                        }
                    }
                },
                'CAR': {
                    'name': 'Cordillera Administrative Region (CAR)',
                    'provinces': {
                        'Benguet': {
                            'cities': {
                                'Baguio': ['Aurora Hill', 'Burnham-Legarda', 'Camp Allen', 'Campo Filipino', 'Country Club Village', 'Dizon Subdivision', 'Dominican Hill-Mirador', 'Engineers Hill', 'Happy Hollow', 'Irisan', 'Loakan-Apugan', 'Lourdes Extension', 'Lourdes Lower', 'Lourdes Proper', 'Lualhati', 'Malcolm Square-Perfecto', 'Magsaysay', 'Market Area', 'Middle Quezon Hill', 'Military Cut-off', 'Mines View', 'New Lucban', 'Outlook Drive', 'Pacdal', 'Pinsao-Pilot Project', 'Poliwes', 'Pucsusan', 'Quezon Hill', 'Quirino Hill', 'Rock Quarry', 'Salud Mitra', 'San Antonio', 'San Luis', 'San Roque', 'San Vicente', 'Santa Scholastica', 'Santo Rosario', 'Santo Tomas', 'Scouthill', 'Session Road Area', 'Slaughter House Area', 'South Drive', 'Teodoro Halsema', 'Trancoville', 'Upper Quezon Hill', 'Victoria Village', 'West Quirino Hill']
                            }
                        }
                    }
                },
                'REGION_IV_A': {
                    'name': 'CALABARZON (Region IV-A)',
                    'provinces': {
                        'Laguna': {
                            'cities': {
                                'San Pablo': ['I-A', 'I-B', 'I-C', 'II-A', 'II-B', 'II-C', 'II-D', 'II-E', 'II-F', 'III-A', 'III-B', 'III-C', 'III-D', 'III-E', 'III-F', 'IV-A', 'IV-B', 'IV-C', 'V-A', 'V-B', 'V-C', 'V-D', 'VI-A', 'VI-B', 'VI-C', 'VI-D', 'VI-E', 'VII-A', 'VII-B', 'VII-C', 'VII-D', 'VII-E']
                            }
                        },
                        'Rizal': {
                            'cities': {
                                'Antipolo': ['Beverly Hills', 'Cupang', 'Dalig', 'De La Paz', 'Dela Paz', 'Fortune', 'Inarawan', 'Mayamot', 'Muntindilaw', 'San Isidro', 'San Jose', 'San Juan', 'San Luis', 'San Roque', 'Santa Cruz', 'Santo Niño', 'Taktak']
                            }
                        },
                        'Batangas': {
                            'cities': {
                                'Batangas City': ['Alangilan', 'Balagtas', 'Balete', 'Banaba Center', 'Banaba East', 'Banaba Ibaba', 'Banaba Kanluran', 'Banaba Silangan', 'Barangay 1', 'Barangay 2', 'Barangay 3', 'Barangay 4', 'Barangay 5', 'Barangay 6', 'Barangay 7', 'Barangay 8', 'Barangay 9', 'Barangay 10', 'Barangay 11', 'Barangay 12', 'Barangay 13', 'Barangay 14', 'Barangay 15', 'Barangay 16', 'Barangay 17', 'Barangay 18', 'Barangay 19', 'Barangay 20', 'Barangay 21', 'Barangay 22', 'Barangay 23', 'Barangay 24', 'Bilogo', 'Bolbok', 'Bukal', 'Calicanto', 'Catandala', 'Concepcion', 'Conde Itaas', 'Conde Labac', 'Cumba', 'Dumantay', 'Dumuclay', 'Gulod Itaas', 'Gulod Labac', 'Haligue Kanluran', 'Haligue Silangan', 'Ilijan', 'Kumba', 'Libjo', 'Liponpon', 'Maapas', 'Mahabang Dahilig', 'Mahabang Parang', 'Malibayo', 'Malitam', 'Maruclap', 'Pallocan Kanluran', 'Pallocan Silangan', 'Pinamucan', 'Pinamucan Ibaba', 'Poblacion', 'Rita', 'San Agapito', 'San Agustin', 'San Andres', 'San Antonio', 'San Isidro', 'San Jose Sico', 'San Miguel', 'Santa Clara', 'Santa Rita Karsada', 'Santa Rita Proper', 'Santo Domingo', 'Santo Niño', 'Santo Tomas', 'Simlong', 'Sirang Lupa', 'Sorosoro Ibaba', 'Sorosoro Ilaya', 'Sorosoro Karsada', 'Tabangao', 'Talahib Pandayan', 'Talahib Payapa', 'Talumpok Kanluran', 'Talumpok Silangan', 'Tingga Itaas', 'Tingga Labac', 'Wawa']
                            }
                        },
                        'Quezon': {
                            'cities': {
                                'Lucena': ['Barangay 1', 'Barangay 2', 'Barangay 3', 'Barangay 4', 'Barangay 5', 'Barangay 6', 'Barangay 7', 'Barangay 8', 'Barangay 9', 'Barangay 10', 'Bocohan', 'Cotta', 'Dalahican', 'Domoit', 'Gulang-Gulang', 'Ibabang Dupay', 'Ibabang Iyam', 'Ibabang Talim', 'Ilayang Dupay', 'Ilayang Iyam', 'Ilayang Talim', 'Isabang', 'Kalumpang', 'Kanlurang Mayao', 'Kulapis', 'Libutad', 'Market View', 'Mayao Castillo', 'Mayao Crossing', 'Mayao Kanluran', 'Mayao Parada', 'Ransohan', 'Sagurong', 'Silangang Mayao', 'Talipan']
                            }
                        }
                    }
                },
                'REGION_V': {
                    'name': 'Bicol Region (Region V)',
                    'provinces': {
                        'Albay': {
                            'cities': {
                                'Legazpi': ['Bagong Abre', 'Banquerohan', 'Bariis', 'Bascaran', 'Bitano', 'Bogtong', 'Bonot', 'Buenavista', 'Cabagñan', 'Cabangan', 'Cruzada', 'Dap-dap', 'Dita', 'Estanza', 'Gogon', 'Guadalupe', 'Homapon', 'Ilawod', 'Kapantawan', 'Kawit-East', 'Kawit-West', 'Lamba', 'Landang', 'Lapu-lapu', 'Lourdes', 'Mabinit', 'Maoyod', 'Mariawa', 'Matanag', 'Oro Site', 'Pinaric', 'PNR-Site', 'Poblacion', 'Portrerro', 'Rawis', 'Sagrada Familia', 'San Joaquin', 'San Rafael', 'San Roque', 'Santa Cruz', 'Serranzana', 'Tula-tula Grande', 'Tula-tula Pequeño', 'Victory Village North', 'Victory Village South', 'Washington Drive', 'Yabo']
                            }
                        },
                        'Camarines Sur': {
                            'cities': {
                                'Naga': ['Abella', 'Bagumbayan North', 'Bagumbayan South', 'Balatas', 'Calauag', 'Cararayan', 'Carolina', 'Concepcion Grande', 'Concepcion Pequeña', 'Dayangdang', 'Del Rosario', 'Dinaga', 'Igualdad Interior', 'Lerma', 'Liboton', 'Mabolo', 'Pacol', 'Panicuason', 'Peñafrancia', 'Poblacion I', 'Poblacion II', 'Poblacion III', 'Poblacion IV', 'Sabang', 'San Felipe', 'San Francisco', 'San Isidro', 'Tabuco', 'Tinago', 'Triangulo']
                            }
                        }
                    }
                }
            }
        }
        
        return jsonify({'success': True, 'data': philippines_data})
        
    except Exception as e:
        print(f'Error getting Philippines address data: {e}')
        return jsonify({'error': 'Failed to get address data'}), 500
# @login_required
# def payment():
#     """Display payment page"""
#     nav_items = get_nav_items()
#     cart_items = []  # TODO: Fetch cart items from session/database
#     
#     # Calculate summary values
#     subtotal = 0
#     discount = 0
#     delivery_fee = 0
#     total = 0
#     
#     if cart_items:
#         subtotal = sum(float(item.get('price', 0)) * int(item.get('quantity', 1)) for item in cart_items)
#         discount = subtotal * 0.2  # 20% discount
#         delivery_fee = 15
#         total = subtotal - discount + delivery_fee
#     
#     return render_template(
#         'main/payment.html',
#         nav_items=nav_items,
#         user=current_user,
#         cart_items=cart_items,
#         subtotal=subtotal,
#         discount=discount,
#         delivery_fee=delivery_fee,
#         total=total
#     )

@main.route('/order-success')
@login_required
def order_success():
    """Show order confirmation with actual order details from database"""
    from project.models import Order, OrderItem
    nav_items = get_nav_items()

    order_number = session.get('latest_order_number')
    if not order_number:
        # Fallback to a default if no order number in session
        order_number = f"DIO-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    # Fetch the actual order from the database
    order = Order.query.filter_by(order_number=order_number, buyer_id=current_user.id).first()
    
    print(f"DEBUG: Looking for order {order_number} for user {current_user.id}")
    print(f"DEBUG: Order found: {order is not None}")
    
    if order:
        # Get order items
        order_items = OrderItem.query.filter_by(order_id=order.id).all()
        
        print(f"DEBUG: Found {len(order_items)} order items for order {order.id}")
        
        # Calculate totals from actual order data
        total_items = sum(item.quantity for item in order_items)
        subtotal = sum(item.total_price for item in order_items)
        delivery_fee = order.shipping_fee or 0
        total = order.total_amount or (subtotal + delivery_fee)
        
        order_summary = {
            'order_number': order.order_number,
            'items_count': total_items,
            'subtotal': subtotal,
            'delivery_fee': delivery_fee,
            'total': total,
            'estimated_delivery': session.get('latest_order_eta', '3-5 business days'),
            'order_items': order_items  # Add the actual order items
        }
    else:
        # Fallback if order not found
        order_summary = {
            'order_number': order_number,
            'items_count': 0,
            'subtotal': 0,
            'delivery_fee': 0,
            'total': 0,
            'estimated_delivery': '3-5 business days'
        }

    return render_template(
        'main/order_success.html',
        nav_items=nav_items,
        order_summary=order_summary
    )


@main.route('/place-order', methods=['POST'])
@login_required
def place_order():
    """Create orders from the current user's cart items."""
    from project.models import CartItem, Order, OrderItem, SellerProduct, ProductVariant, VariantSize
    from project import db

    try:
        user = current_user
        if not user or not user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401

        # Get form data (shipping and payment information)
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        print(f"DEBUG: Received order data: {data}")  # Debug log
        
        # Extract shipping information
        shipping_info = {
            'first_name': data.get('firstName', ''),
            'last_name': data.get('lastName', ''),
            'email': data.get('email', ''),
            'address': data.get('address', ''),
            'apartment': data.get('apartment', ''),
            'city': data.get('city', ''),
            'state': data.get('state', ''),
            'zip_code': data.get('zipCode', ''),
            'phone': data.get('phone', ''),
            'country': data.get('country', '')
        }
        
        # Extract payment information
        payment_info = {
            'method': data.get('paymentMethod', ''),
            'card_number': data.get('cardNumber', ''),
            'expiry': data.get('expiry', ''),
            'cvc': data.get('cvc', ''),
            'cardholder_name': data.get('cardholderName', ''),
            'gcash_number': data.get('gcashNumber', '')
        }

        # Fetch cart items for the user
        cart_items = CartItem.query.filter_by(user_id=user.id).all()
        if not cart_items:
            return jsonify({'error': 'No items in cart'}), 400
        
        print(f"DEBUG: Found {len(cart_items)} cart items for user {user.id}")  # Debug log

        # Group by seller_id
        groups = {}
        for it in cart_items:
            groups.setdefault(it.seller_id, []).append(it)

        created_orders = []
        for seller_id, items in groups.items():
            try:
                # Ensure clean session state
                db.session.rollback()  # Clear any pending state
                
                print(f"DEBUG: Processing order for seller {seller_id} with {len(items)} items")
                order_number = f"DIO-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{seller_id}"
                subtotal = 0
                for it in items:
                    subtotal += float(it.product_price or 0) * int(it.quantity or 1)

                delivery_fee = 0 if subtotal >= 1500 or subtotal == 0 else 150
                total_amount = subtotal + delivery_fee

                order = Order(
                    order_number=order_number,
                    buyer_id=user.id,
                    seller_id=seller_id,
                    total_amount=total_amount,
                    shipping_fee=delivery_fee,
                    tax_amount=0,
                    discount_amount=0,
                    status='pending',
                    payment_status='pending' if payment_info['method'] == 'cod' else 'paid',
                    shipping_address={
                        'first_name': shipping_info['first_name'],
                        'last_name': shipping_info['last_name'],
                        'email': shipping_info['email'],
                        'address': shipping_info['address'],
                        'apartment': shipping_info['apartment'],
                        'city': shipping_info['city'],
                        'state': shipping_info['state'],
                        'zip_code': shipping_info['zip_code'],
                        'phone': shipping_info['phone'],
                        'country': shipping_info['country']
                    },
                    billing_address={
                        'payment_method': payment_info['method'],
                        'card_number_last4': payment_info['card_number'][-4:] if payment_info['card_number'] else '',
                        'cardholder_name': payment_info['cardholder_name'],
                        'gcash_number': payment_info['gcash_number'],
                        'payment_status': 'processed'
                    }
                )
                db.session.add(order)
                db.session.flush()

                # Create OrderItems and adjust stock
                for it in items:
                    oi = OrderItem(
                        order_id=order.id,
                        product_id=it.product_id,
                        seller_id=it.seller_id or seller_id,
                        product_name=it.product_name,
                        product_image=it.variant_image,  # Now this field exists in the database
                        variant_name=f"{it.color} · {it.size}",
                        size=it.size,
                        color=it.color,
                        quantity=it.quantity,
                        unit_price=it.product_price,
                        total_price=(float(it.product_price or 0) * int(it.quantity or 1))
                    )
                    db.session.add(oi)

                    # Try to decrement VariantSize if it exists
                    try:
                        pv = ProductVariant.query.filter_by(product_id=it.product_id, variant_name=it.color).first()
                        if pv:
                            vs = VariantSize.query.filter_by(variant_id=pv.id, size_label=it.size).first()
                            if vs:
                                vs.stock_quantity = max(0, (vs.stock_quantity or 0) - int(it.quantity or 0))
                                db.session.add(vs)
                    except Exception:
                        pass

                    # Update seller product total_stock if present
                    try:
                        sp = SellerProduct.query.get(it.product_id)
                        if sp and sp.total_stock is not None:
                            sp.total_stock = max(0, (sp.total_stock or 0) - int(it.quantity or 0))
                            db.session.add(sp)
                    except Exception:
                        pass

                # Commit order and remove cart items
                db.session.commit()
                created_orders.append(order_number)
                print(f"DEBUG: Successfully created order {order_number}")
                
                # Remove cart items for this seller
                for it in items:
                    try:
                        db.session.delete(it)
                    except Exception:
                        pass
                db.session.commit()
            
            except Exception as e:
                print(f"ERROR: Failed to create order for seller {seller_id}: {str(e)}")
                print(f"ERROR Details: {type(e).__name__}: {e}")
                import traceback
                print(f"ERROR Traceback: {traceback.format_exc()}")
                db.session.rollback()  # Ensure clean rollback
                continue

        # Clear session cart cache
        session.pop('cart_items', None)
        latest_order_number = created_orders[0] if created_orders else f"DIO-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        session['latest_order_number'] = latest_order_number
        session['latest_order_eta'] = '3-5 business days'

        return jsonify({'success': True, 'order_numbers': created_orders, 'order_number': latest_order_number})

    except Exception as e:
        print('Error placing order:', e)
        db.session.rollback()
        return jsonify({'error': 'Failed to place order'}), 500

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

    # Calculate product ratings
    product_rating = 0.0
    rating_count = 0
    
    try:
        from project.models import ProductReview
        from sqlalchemy import func
        
        # Get rating data for this product
        rating_data = db.session.query(
            func.avg(ProductReview.rating).label('avg_rating'),
            func.count(ProductReview.id).label('count')
        ).filter_by(product_id=product.get('id')).first()
        
        if rating_data and rating_data.avg_rating:
            product_rating = round(float(rating_data.avg_rating), 1)
            rating_count = rating_data.count
        else:
            # Fallback: generate some sample data for display
            import random
            product_rating = round(random.randint(35, 50) / 10.0, 1)
            rating_count = random.randint(15, 250)
    except Exception as e:
        print(f"Error calculating ratings: {e}")
        # Use sample data as fallback
        import random
        product_rating = round(random.randint(35, 50) / 10.0, 1)
        rating_count = random.randint(15, 250)

    return render_template(
        'main/product_detail.html',
        nav_items=nav_items,
        product=product,
        stock_data=stock_data,
        variant_photos=variant_photos,
        product_price=product_price,
        selected_quantity=selected_quantity,
        seller_info=seller_info,
        product_rating=product_rating,
        rating_count=rating_count,
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
    try:
        seller_profile = Seller.query.filter_by(business_name=store_name.replace('-', ' ')).first()
        if not seller_profile:
            flash('Store not found', 'error')
            return redirect(url_for('main.index'))

        # Redirect to the ID-based store page (store_page expects a user id)
        return redirect(url_for('main.store_page', seller_id=seller_profile.user_id))
    except Exception as e:
        print(f"Error in store_page_by_name: {e}")
        flash('Error locating store', 'error')
        return redirect(url_for('main.index'))

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


@main.route('/shop/clothing')
def shop_all_clothing():
    """Show all clothing products (category landing)."""
    nav_items = get_nav_items()
    products = fetch_products(category='clothing', limit=48)
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='clothing', selected_category='clothing')

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
        variant = None
        try:
            variant_list = ProductVariant.query.filter_by(
                product_id=product_id,
                variant_name=color
            ).all()
            variant = variant_list[0] if variant_list else None
        except Exception as e:
            print(f"Warning: ProductVariant query failed in get_product_sizes_for_color: {e}")

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


@main.route('/api/seller/<int:seller_id>/products')
def api_seller_products(seller_id):
    """API: Return products from a specific seller for recommendations"""
    try:
        limit = int(request.args.get('limit', 4))
        exclude_id = request.args.get('exclude_id')
        
        # Get products from this seller
        query = SellerProduct.query.filter_by(seller_id=seller_id, status='active', is_draft=False)
        
        # Exclude the current product if specified
        if exclude_id:
            try:
                exclude_id = int(exclude_id)
                query = query.filter(SellerProduct.id != exclude_id)
            except ValueError:
                pass
        
        products = query.order_by(SellerProduct.created_at.desc()).limit(limit).all()
        
        # Convert to public dict format
        items = []
        for sp in products:
            items.append({
                'id': sp.id,
                'name': sp.name,
                'primaryImage': _normalize_image_path(sp.primary_image) or '/static/image/banner_1.png',
                'price': float(sp.price or 0),
                'originalPrice': float(sp.compare_at_price) if sp.compare_at_price and sp.compare_at_price > sp.price else None,
                'category': sp.category,
                'subcategory': sp.subcategory,
            })
        
        return jsonify({'products': items, 'count': len(items)})
        
    except Exception as e:
        print(f"Error getting seller products: {e}")
        return jsonify({'error': 'Failed to get seller products'}), 500