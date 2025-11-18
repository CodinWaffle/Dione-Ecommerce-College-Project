"""
Main routes for Dione Ecommerce
"""
from flask import Blueprint, render_template, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user
from project import db
from project.models import User

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
            return redirect(url_for('main.seller_dashboard'))
        if role == 'rider':
            return redirect(url_for('main.rider_dashboard'))
    
    # Navigation items for header
    nav_items = [
        {
            'name': 'Clothing',
            'bold': False,
            'active': True,
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
    
    return render_template('main/index.html', nav_items=nav_items)

@main.route('/profile')
@login_required
def profile():
    role = (getattr(current_user, 'role', '') or 'buyer').lower()
    if getattr(current_user, 'role_requested', None) and not getattr(current_user, 'is_approved', True):
        return redirect(url_for('main.pending'))
    if role == 'seller':
        return redirect(url_for('main.seller_dashboard'))
    if role == 'rider':
        return redirect(url_for('main.rider_dashboard'))
    return render_template('main/profile.html', username=current_user.email)

@main.route('/seller/dashboard')
@login_required
def seller_dashboard():
    role = (getattr(current_user, 'role', '') or '').lower()
    is_approved = getattr(current_user, 'is_approved', False)
    
    # If user has requested seller role but not approved yet, show pending page
    if getattr(current_user, 'role_requested', None) == 'seller' and not is_approved:
        return redirect(url_for('main.pending'))
    
    # If user is not a seller, deny access
    if role != 'seller' or not is_approved:
        flash("You don't have access to the seller dashboard.", 'warning')
        return redirect(url_for('main.profile'))
    
    # Get seller profile data
    seller_profile = current_user.seller_profile[0] if hasattr(current_user, 'seller_profile') and current_user.seller_profile else None
    
    return render_template('seller/dashboard.html', 
                         username=current_user.email, 
                         seller=seller_profile,
                         active_page='dashboard')


@main.route('/seller/products')
@login_required
def seller_products():
    if (getattr(current_user, 'role', '') or '').lower() != 'seller' or not getattr(current_user, 'is_approved', False):
        flash("You don't have access to seller tools.", 'warning')
        return redirect(url_for('main.profile'))
    
    # Get seller profile data
    seller_profile = current_user.seller_profile[0] if hasattr(current_user, 'seller_profile') and current_user.seller_profile else None
    
    return render_template('seller/seller_product_management.html', 
                         username=current_user.email, 
                         seller=seller_profile,
                         active_page='products')

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
        return redirect(url_for('main.seller_dashboard'))
    if role == 'rider':
        return redirect(url_for('main.rider_dashboard'))
    return redirect(url_for('main.index'))



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
