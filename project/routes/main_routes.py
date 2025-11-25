"""
Main routes for Dione Ecommerce
"""
from flask import Blueprint, render_template, jsonify, redirect, url_for, flash
from flask import request
from flask_login import login_required, current_user, logout_user
from project import db
from project.models import Product, User, SellerProduct
from sqlalchemy import func

main = Blueprint('main', __name__)

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
            'primaryImage': sp.primary_image or '/static/image/banner.png',
            'secondaryImage': sp.secondary_image or sp.primary_image or '/static/image/banner.png',
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
        items.append(p.to_public_dict())
    
    for sp in seller_products:
        # Convert SellerProduct to public dict format compatible with frontend
        items.append({
            'id': sp.id,
            'name': sp.name,
            'primaryImage': sp.primary_image or '/static/image/banner.png',
            'secondaryImage': sp.secondary_image or sp.primary_image or '/static/image/banner.png',
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
        if isinstance(sp.variants, list):
            variant = None
            for v in sp.variants:
                if str(v.get('color', '')) == str(variant_id):
                    variant = v
                    break
            
            if not variant:
                return jsonify({'error': 'Variant not found'}), 404
                
            return jsonify({
                'variant': {
                    'color': variant.get('color'),
                    'images': {
                        'primary': sp.primary_image or '/static/image/banner.png',
                        'secondary': sp.secondary_image or sp.primary_image or '/static/image/banner.png'
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
                if isinstance(sp.variants, list):
                    # Convert list of variants to structured data
                    for variant in sp.variants:
                        if isinstance(variant, dict):
                            color = variant.get('color', 'Unknown')
                            size = variant.get('size', 'OS')
                            stock = variant.get('stock', 0)
                            color_hex = variant.get('colorHex', '#000000')
                            
                            # Initialize color in stock_data if not exists
                            if color not in stock_data:
                                stock_data[color] = {}
                            
                            # Add size stock for this color
                            stock_data[color][size] = stock
                            
                            # Set color hex for styling (store in variant_photos for now)
                            if color not in variant_photos:
                                variant_photos[color] = {
                                    'primary': sp.primary_image or '/static/image/banner.png',
                                    'secondary': sp.secondary_image or sp.primary_image or '/static/image/banner.png',
                                    'color_hex': color_hex
                                }
                elif isinstance(sp.variants, dict):
                    # Handle existing dict structure
                    for k, v in sp.variants.items():
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

            # fallback to top-level images
            primary = sp.primary_image or sp.primary_image
            secondary = sp.secondary_image or sp.primary_image

            payload = {
                'id': sp.id,
                'name': sp.name,
                'description': sp.description,
                'price': float(sp.price or 0),
                'originalPrice': float(sp.compare_at_price) if sp.compare_at_price and sp.compare_at_price > sp.price else None,
                'primaryImage': primary or '/static/image/banner.png',
                'secondaryImage': secondary or primary or '/static/image/banner.png',
                'materials': sp.materials,
                'variants': sp.variants or {},
                'variant_photos': variant_photos,
                'stock_data': stock_data,
                'type': 'seller'
            }
            return jsonify({'product': payload})

        # Try legacy Product model
        p = Product.query.get(product_id)
        if p:
            payload = p.to_public_dict()
            payload.update({
                'description': p.description,
                'materials': p.materials,
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
    """Display shopping cart"""
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
        'main/cart.html',
        nav_items=nav_items,
        cart_items=cart_items,
        subtotal=subtotal,
        discount=discount,
        delivery_fee=delivery_fee,
        total=total
    )

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

    try:
        # Try SellerProduct (more detailed model)
        try:
            sp = SellerProduct.query.get(int(product_id))
        except Exception:
            sp = None

        if sp:
            # Build variant_photos and stock_data from variants JSON
            try:
                if isinstance(sp.variants, list):
                    # Convert list of variants to structured data
                    for variant in sp.variants:
                        if isinstance(variant, dict):
                            color = variant.get('color', 'Unknown')
                            size = variant.get('size', 'OS')
                            stock = variant.get('stock', 0)
                            color_hex = variant.get('colorHex', '#000000')
                            
                            # Initialize color in stock_data if not exists
                            if color not in stock_data:
                                stock_data[color] = {}
                            
                            # Add size stock for this color
                            stock_data[color][size] = stock
                            
                            # Set color hex for styling (store in variant_photos for now)
                            if color not in variant_photos:
                                variant_photos[color] = {
                                    'primary': sp.primary_image or '/static/image/banner.png',
                                    'secondary': sp.secondary_image or sp.primary_image or '/static/image/banner.png',
                                    'color_hex': color_hex
                                }
                elif isinstance(sp.variants, dict):
                    # Handle existing dict structure
                    for color_key, v in sp.variants.items():
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
            product = {
                'id': sp.id,
                'name': sp.name,
                'description': sp.description or '',
                'price': float(sp.price or 0),
                'originalPrice': float(sp.compare_at_price) if sp.compare_at_price and sp.compare_at_price > sp.price else None,
                'primaryImage': primary,
                'secondaryImage': secondary,
                'materials': sp.materials,
                'variants': sp.variants or {},
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
    )


@main.route('/store/<store_name>')
def store_page(store_name):
    """Render a storefront page for the given store name (simple lookup by name).

    This is a lightweight route so clicking the store name in product dropdown
    can display the `main/store_page.html` template. In a full implementation
    this should lookup a Seller/Store model by id or slug.
    """
    nav_items = get_nav_items()
    display_name = (store_name or 'Store').replace('-', ' ')
    # For now use a default location; real data should come from the DB
    store_location = 'Makati City, Metro Manila'

    # Sample stats (replace with DB lookups for real data)
    products_sold = 1200
    followers = 8500

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
            # remove trailing .0
            s = f"{v}K"
            if s.endswith('.0K'):
                s = s.replace('.0K', 'K')
            return s
        return str(n)

    products_sold_display = fmt_count(products_sold)
    followers_display = fmt_count(followers)

    return render_template(
        'main/store_page.html',
        nav_items=nav_items,
        store_name=display_name,
        store_location=store_location,
        products_sold_display=products_sold_display,
        followers_display=followers_display,
        products_sold=products_sold,
        followers=followers,
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
