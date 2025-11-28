"""
Main routes for Dione Ecommerce
"""
from flask import Blueprint, render_template, jsonify, redirect, url_for, flash, current_app
from flask import request
from flask_login import login_required, current_user, logout_user
from project import db
from project.models import Product, User, SellerProduct, ProductReport, Seller
from sqlalchemy import func
import hashlib

main = Blueprint('main', __name__)


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
    if s.startswith('/') or s.startswith('http'):
        return s
    return '/static/' + s.lstrip('/')

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
            'primaryImage': _normalize_image_path(sp.primary_image) or '/static/image/banner.png',
            'secondaryImage': _normalize_image_path(sp.secondary_image) or _normalize_image_path(sp.primary_image) or '/static/image/banner.png',
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
            'primaryImage': _normalize_image_path(sp.primary_image) or '/static/image/banner.png',
            'secondaryImage': _normalize_image_path(sp.secondary_image) or _normalize_image_path(sp.primary_image) or '/static/image/banner.png',
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
                        'primary': _normalize_image_path(sp.primary_image) or '/static/image/banner.png',
                        'secondary': _normalize_image_path(sp.secondary_image) or _normalize_image_path(sp.primary_image) or '/static/image/banner.png'
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
                                    'primary': _normalize_image_path(sp.primary_image) or '/static/image/banner.png',
                                    'secondary': _normalize_image_path(sp.secondary_image) or _normalize_image_path(sp.primary_image) or '/static/image/banner.png',
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
            primary = _normalize_image_path(sp.primary_image) or '/static/image/banner.png'
            secondary = _normalize_image_path(sp.secondary_image) or _normalize_image_path(sp.primary_image) or '/static/image/banner.png'

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
            'primaryImage': sp.primary_image or '/static/image/banner.png',
            'secondaryImage': sp.secondary_image or sp.primary_image or '/static/image/banner.png',
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
    
    # Get cart items from session
    cart_items = session.get('cart_items', [])
    
    # Group cart items by store
    stores_with_items = {}
    
    for item in cart_items:
        try:
            # Get product and seller information
            product = SellerProduct.query.get(item.get('product_id'))
            if product:
                seller_user = User.query.get(product.seller_id)
                if seller_user and seller_user.seller_profile:
                    seller_profile = seller_user.seller_profile[0]
                    store_id = seller_user.id
                    store_name = seller_profile.business_name
                    
                    # Get variant photo
                    variant_photo = item.get('image_url', product.primary_image or '/static/image/banner.png')
                    
                    # Create enhanced item data
                    enhanced_item = {
                        'id': item.get('id', f"{item.get('product_id')}_{item.get('color')}_{item.get('size')}"),
                        'product_id': item.get('product_id'),
                        'name': product.name,
                        'price': float(product.price),
                        'quantity': item.get('quantity', 1),
                        'color': item.get('color', 'Default'),
                        'size': item.get('size', 'One Size'),
                        'image_url': variant_photo,
                        'color_hex': item.get('color_hex', '#000000')
                    }
                    
                    # Group by store
                    if store_id not in stores_with_items:
                        stores_with_items[store_id] = {
                            'store_info': {
                                'id': store_id,
                                'name': store_name,
                                'is_verified': seller_profile.is_verified,
                                'avatar': '/static/image/default-store.png'  # TODO: Add store avatar
                            },
                            'items': []
                        }
                    
                    stores_with_items[store_id]['items'].append(enhanced_item)
        except Exception as e:
            print(f"Error processing cart item: {e}")
            continue
    
    # Calculate summary values
    subtotal = 0
    total_items = 0
    
    for store_data in stores_with_items.values():
        for item in store_data['items']:
            item_total = item['price'] * item['quantity']
            subtotal += item_total
            total_items += item['quantity']
    
    discount = subtotal * 0.2 if subtotal > 0 else 0  # 20% discount
    delivery_fee = 15 if subtotal > 0 else 0
    total = subtotal - discount + delivery_fee if subtotal > 0 else 0
    
    return render_template(
        'main/cart.html',
        nav_items=nav_items,
        stores_with_items=stores_with_items,
        total_items=total_items,
        subtotal=subtotal,
        discount=discount,
        delivery_fee=delivery_fee,
        total=total
    )

@main.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    """Add item to cart with variant information"""
    from flask import session, request, jsonify
    
    try:
        data = request.get_json()
        
        # Extract item data
        product_id = data.get('product_id')
        color = data.get('color')
        size = data.get('size')
        quantity = int(data.get('quantity', 1))
        color_hex = data.get('color_hex', '#000000')
        image_url = data.get('image_url')
        
        # Validate required fields
        if not all([product_id, color, size]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Get or create cart items in session
        cart_items = session.get('cart_items', [])
        
        # Create unique item ID
        item_id = f"{product_id}_{color}_{size}"
        
        # Check if item already exists in cart
        existing_item = None
        for item in cart_items:
            if (item.get('product_id') == product_id and 
                item.get('color') == color and 
                item.get('size') == size):
                existing_item = item
                break
        
        if existing_item:
            # Update quantity
            existing_item['quantity'] += quantity
        else:
            # Add new item
            new_item = {
                'id': item_id,
                'product_id': product_id,
                'color': color,
                'size': size,
                'quantity': quantity,
                'color_hex': color_hex,
                'image_url': image_url,
                'added_at': datetime.now().isoformat()
            }
            cart_items.append(new_item)
        
        # Save to session
        session['cart_items'] = cart_items
        session.permanent = True
        
        return jsonify({
            'success': True,
            'message': 'Item added to cart',
            'cart_count': sum(item['quantity'] for item in cart_items)
        })
        
    except Exception as e:
        print(f"Error adding to cart: {e}")
        return jsonify({'error': 'Failed to add item to cart'}), 500

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

@main.route('/my-purchases')
@login_required
def my_purchases():
    """Display user's purchase history and reviews"""
    nav_items = get_nav_items()
    
    # TODO: Fetch actual orders from database
    # For now, using sample data structure
    sample_orders = [
        {
            'id': 'ORD-2024-001',
            'date': 'November 20, 2024',
            'status': 'delivered',
            'total': 914.00,
            'items': [
                {
                    'id': 1,
                    'name': 'Premium Cotton T-Shirt',
                    'variant': 'Color: Navy Blue, Size: M',
                    'price': 899.00,
                    'quantity': 1,
                    'image': '/static/image/banner.png'
                }
            ],
            'reviews': [
                {
                    'reviewer': 'Maria S.',
                    'date': 'November 22, 2024',
                    'ratings': {'product': 5, 'store': 4, 'delivery': 5},
                    'content': 'Excellent quality t-shirt! The fabric is soft and comfortable.',
                    'photos': ['/static/image/banner.png', '/static/image/banner.png']
                }
            ]
        },
        {
            'id': 'ORD-2024-002',
            'date': 'November 25, 2024',
            'status': 'processing',
            'total': 1314.00,
            'items': [
                {
                    'id': 2,
                    'name': 'Casual Denim Jeans',
                    'variant': 'Color: Dark Blue, Size: 32',
                    'price': 1299.00,
                    'quantity': 1,
                    'image': '/static/image/banner.png'
                }
            ],
            'reviews': []
        }
    ]
    
    return render_template(
        'main/my_purchases.html',
        nav_items=nav_items,
        orders=sample_orders
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
                        
                        # Calculate followers count (placeholder - implement when follow system is added)
                        followers_count = 1250  # TODO: Get from actual followers table
                        
                        # Format joined date
                        joined_date = seller_user.created_at.strftime('%B %Y') if seller_user.created_at else 'Recently'
                        
                        seller_info = {
                            'id': seller_user.id,
                            'business_name': seller_profile.business_name,
                            'business_address': seller_profile.business_address,
                            'business_city': seller_profile.business_city,
                            'business_country': seller_profile.business_country,
                            'store_description': seller_profile.store_description,
                            'is_verified': seller_profile.is_verified,
                            'rating': avg_rating,
                            'products_count': products_count,
                            'followers_count': followers_count,
                            'joined_date': joined_date,
                            'created_at': seller_user.created_at
                        }
            except Exception as e:
                print(f"Error fetching seller info: {e}")
                seller_info = None
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

    except Exception:
        # Ensure we always return a usable template even on errors
        product = product or {}

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
        
        # Calculate seller statistics
        from sqlalchemy import func
        
        # Count products by this seller
        products_count = SellerProduct.query.filter_by(
            seller_id=seller_user.id, 
            status='active'
        ).count()
        
        # Calculate average rating (placeholder)
        avg_rating = 4.5  # TODO: Calculate from actual reviews
        
        # Calculate followers count (placeholder)
        followers_count = 1250  # TODO: Get from actual followers table
        
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
                'store_description': seller_profile.store_description,
                'is_verified': seller_profile.is_verified,
                'rating': avg_rating,
                'products_count': products_count,
                'followers_count': followers_count,
                'joined_date': joined_date
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
