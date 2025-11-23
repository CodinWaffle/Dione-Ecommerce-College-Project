"""
Main routes for Dione Ecommerce
"""
from flask import Blueprint, render_template, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user
from project import db
from project.models import Product, User

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
    
    featured = Product.query.filter_by(status='active').order_by(Product.created_at.desc()).limit(8).all()
    trending = Product.query.filter_by(status='active').order_by(Product.stock.desc()).limit(8).all()
    new_arrivals = Product.query.filter_by(status='active').order_by(Product.updated_at.desc()).limit(8).all()

    product_buckets = {
        'featured': [product.to_public_dict() for product in featured],
        'trending': [product.to_public_dict() for product in trending],
        'new_arrivals': [product.to_public_dict() for product in new_arrivals],
    }
    
    return render_template('main/index.html', nav_items=nav_items, product_buckets=product_buckets)

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
    return render_template('rider/dashboard.html', username=current_user.email)

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
    product = {}  # TODO: Fetch product from database by ID
    
    # Stock data structure: color -> sizes -> quantity
    stock_data = {
        'Black': {'XS': 5, 'S': 8, 'M': 10, 'L': 7, 'XL': 4},
        'White': {'XS': 3, 'S': 6, 'M': 9, 'L': 5, 'XL': 2},
        'Navy': {'XS': 4, 'S': 7, 'M': 8, 'L': 6, 'XL': 3},
        'Yellow': {'XS': 2, 'S': 5, 'M': 6, 'L': 4, 'XL': 1}
    }
    
    # Product pricing and cart popup data
    product_price = 99.99  # TODO: Fetch actual price from database
    selected_quantity = 1
    
    return render_template(
        'main/product_detail.html',
        nav_items=nav_items,
        product=product,
        stock_data=stock_data,
        product_price=product_price,
        selected_quantity=selected_quantity
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

@main.route('/shop/all/clothing')
def shop_all_clothing():
    """Shop all clothing items"""
    products = []  # TODO: Fetch from database
    nav_items = get_nav_items()
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='clothing', selected_category='clothing')

@main.route('/shop/clothing/tops')
def shop_clothing_tops():
    """Shop clothing tops"""
    products = []
    nav_items = get_nav_items()
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='clothing', subcategory='tops', selected_category='clothing')

@main.route('/shop/clothing/bottoms')
def shop_clothing_bottoms():
    """Shop clothing bottoms"""
    products = []
    nav_items = get_nav_items()
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='clothing', subcategory='bottoms', selected_category='clothing')

@main.route('/shop/clothing/dresses')
def shop_clothing_dresses():
    """Shop dresses"""
    products = []
    nav_items = get_nav_items()
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='clothing', subcategory='dresses', selected_category='clothing')

@main.route('/shop/clothing/outwear')
def shop_clothing_outwear():
    """Shop outerwear"""
    products = []
    nav_items = get_nav_items()
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='clothing', subcategory='outwear', selected_category='clothing')

@main.route('/shop/clothing/activewear')
def shop_clothing_activewear():
    """Shop activewear"""
    products = []
    nav_items = get_nav_items()
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='clothing', subcategory='activewear', selected_category='clothing')

@main.route('/shop/clothing/sleepwear')
def shop_clothing_sleepwear():
    """Shop sleepwear"""
    products = []
    nav_items = get_nav_items()
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='clothing', subcategory='sleepwear', selected_category='clothing')

@main.route('/shop/clothing/undergarments')
def shop_clothing_undergarments():
    """Shop undergarments"""
    products = []
    nav_items = get_nav_items()
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='clothing', subcategory='undergarments', selected_category='clothing')

@main.route('/shop/clothing/swimwear')
def shop_clothing_swimwear():
    """Shop swimwear"""
    products = []
    nav_items = get_nav_items()
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='clothing', subcategory='swimwear', selected_category='clothing')

@main.route('/shop/clothing/occasionwear')
def shop_clothing_occasionwear():
    """Shop occasionwear"""
    products = []
    nav_items = get_nav_items()
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='clothing', subcategory='occasionwear', selected_category='clothing')


# ============================================
# SHOES ROUTES
# ============================================

@main.route('/shop/all/shoes')
def shop_all_shoes():
    """Shop all shoes"""
    products = []
    nav_items = get_nav_items()
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='shoes', selected_category='shoes')

@main.route('/shop/shoes/heels')
def shop_shoes_heels():
    """Shop heels"""
    products = []
    nav_items = get_nav_items()
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='shoes', subcategory='heels', selected_category='shoes')

@main.route('/shop/shoes/flats')
def shop_shoes_flats():
    """Shop flats"""
    products = []
    nav_items = get_nav_items()
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='shoes', subcategory='flats', selected_category='shoes')

@main.route('/shop/shoes/sandals')
def shop_shoes_sandals():
    """Shop sandals"""
    products = []
    nav_items = get_nav_items()
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='shoes', subcategory='sandals', selected_category='shoes')

@main.route('/shop/shoes/sneakers')
def shop_shoes_sneakers():
    """Shop sneakers"""
    products = []
    nav_items = get_nav_items()
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='shoes', subcategory='sneakers', selected_category='shoes')

@main.route('/shop/shoes/boots')
def shop_shoes_boots():
    """Shop boots"""
    products = []
    nav_items = get_nav_items()
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='shoes', subcategory='boots', selected_category='shoes')

@main.route('/shop/shoes/slippers')
def shop_shoes_slippers():
    """Shop slippers & comfort wear"""
    products = []
    nav_items = get_nav_items()
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='shoes', subcategory='slippers', selected_category='shoes')

@main.route('/shop/shoes/occasion-shoes')
def shop_shoes_occasion_shoes():
    """Shop occasion/dress shoes"""
    products = []
    nav_items = get_nav_items()
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='shoes', subcategory='occasion-shoes', selected_category='shoes')


# ============================================
# ACCESSORIES ROUTES
# ============================================

@main.route('/shop/all/accessories')
def shop_all_accessories():
    """Shop all accessories"""
    products = []
    nav_items = get_nav_items()
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='accessories', selected_category='accessories')

@main.route('/shop/accessories/bags')
def shop_accessories_bags():
    """Shop bags"""
    products = []
    nav_items = get_nav_items()
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='accessories', subcategory='bags', selected_category='accessories')

@main.route('/shop/accessories/jewelry')
def shop_accessories_jewelry():
    """Shop jewelry"""
    products = []
    nav_items = get_nav_items()
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='accessories', subcategory='jewelry', selected_category='accessories')

@main.route('/shop/accessories/hair-accessories')
def shop_accessories_hair_accessories():
    """Shop hair accessories"""
    products = []
    nav_items = get_nav_items()
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='accessories', subcategory='hair-accessories', selected_category='accessories')

@main.route('/shop/accessories/belts')
def shop_accessories_belts():
    """Shop belts"""
    products = []
    nav_items = get_nav_items()
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='accessories', subcategory='belts', selected_category='accessories')

@main.route('/shop/accessories/scarves-wraps')
def shop_accessories_scarves_wraps():
    """Shop scarves & wraps"""
    products = []
    nav_items = get_nav_items()
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='accessories', subcategory='scarves-wraps', selected_category='accessories')

@main.route('/shop/accessories/hats-caps')
def shop_accessories_hats_caps():
    """Shop hats & caps"""
    products = []
    nav_items = get_nav_items()
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='accessories', subcategory='hats-caps', selected_category='accessories')

@main.route('/shop/accessories/eyewear')
def shop_accessories_eyewear():
    """Shop eyewear"""
    products = []
    nav_items = get_nav_items()
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='accessories', subcategory='eyewear', selected_category='accessories')

@main.route('/shop/accessories/watches')
def shop_accessories_watches():
    """Shop watches"""
    products = []
    nav_items = get_nav_items()
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='accessories', subcategory='watches', selected_category='accessories')

@main.route('/shop/accessories/gloves')
def shop_accessories_gloves():
    """Shop gloves"""
    products = []
    nav_items = get_nav_items()
    return render_template('main/shop_category.html', products=products, nav_items=nav_items, category='accessories', subcategory='gloves', selected_category='accessories')

@main.route('/shop/accessories/others')
def shop_accessories_others():
    """Shop other accessories"""
    products = []
    nav_items = get_nav_items()
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
