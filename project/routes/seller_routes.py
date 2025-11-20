"""
Seller routes for managing products, orders, and seller dashboard
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from project import db
from project.models import User, Seller

seller_bp = Blueprint('seller', __name__, url_prefix='/seller')


@seller_bp.before_request
@login_required
def restrict_to_seller():
    """Ensure only sellers can access seller routes"""
    if not current_user.is_authenticated:
        flash("Please log in to access seller dashboard.", 'warning')
        return redirect(url_for('auth.login'))
    
    if (getattr(current_user, 'role', '') or '').lower() != 'seller':
        flash("Seller access required.", 'danger')
        return redirect(url_for('main.index'))
    
    if getattr(current_user, 'is_suspended', False):
        flash("Your seller account is suspended.", 'danger')
        return redirect(url_for('main.index'))


@seller_bp.route('/products')
def seller_products():
    """Seller product management page"""
    # Sample product data - this will be replaced with actual database queries
    # when Product model is created
    products = [
        {
            'id': 1,
            'name': 'Classic White T-Shirt',
            'category': 'Clothing',
            'subcategory': 'T-Shirts',
            'price': 29.99,
            'stock': 100,
            'status': 'active',
            'sku': 'PRD-001',
            'image': '/static/image/placeholder-product.jpg'
        },
        {
            'id': 2,
            'name': 'Blue Denim Jeans',
            'category': 'Clothing',
            'subcategory': 'Jeans',
            'price': 59.99,
            'stock': 0,
            'status': 'out-of-stock',
            'sku': 'PRD-002',
            'image': '/static/image/placeholder-product.jpg'
        },
        {
            'id': 3,
            'name': 'Running Shoes',
            'category': 'Footwear',
            'subcategory': 'Sports Shoes',
            'price': 89.99,
            'stock': 45,
            'status': 'active',
            'sku': 'PRD-003',
            'image': '/static/image/placeholder-product.jpg'
        },
        {
            'id': 4,
            'name': 'Leather Wallet',
            'category': 'Accessories',
            'subcategory': 'Wallets',
            'price': 39.99,
            'stock': 75,
            'status': 'active',
            'sku': 'PRD-004',
            'image': '/static/image/placeholder-product.jpg'
        },
        {
            'id': 5,
            'name': 'Summer Dress',
            'category': 'Clothing',
            'subcategory': 'Dresses',
            'price': 49.99,
            'stock': 30,
            'status': 'active',
            'sku': 'PRD-005',
            'image': '/static/image/placeholder-product.jpg'
        }
    ]
    
    # Sample category hierarchy for the category selector
    categories = {
        'Clothing': ['T-Shirts', 'Jeans', 'Dresses', 'Jackets', 'Shorts'],
        'Footwear': ['Sports Shoes', 'Casual Shoes', 'Sandals', 'Boots'],
        'Accessories': ['Wallets', 'Bags', 'Belts', 'Watches', 'Jewelry'],
        'Electronics': ['Phones', 'Laptops', 'Tablets', 'Accessories'],
        'Clothing_details': {
            'T-Shirts': ['V-Neck', 'Crew Neck', 'Polo'],
            'Dresses': ['Casual', 'Formal', 'Party']
        }
    }
    
    return render_template(
        'seller/seller_product_management.html', 
        active_page='products',
        products=products,
        categories=categories
    )


@seller_bp.route('/add_product', methods=['GET', 'POST'])
def add_product():
    """Add new product - Step 1: Basic Information"""
    if request.method == 'POST':
        # Store form data in session
        from flask import session
        if 'product_data' not in session:
            session['product_data'] = {}
        session['product_data'].update(request.form.to_dict())
        session.modified = True
        return redirect(url_for('seller.add_product_description'))
    return render_template('seller/add_product.html')


@seller_bp.route('/add_product_description', methods=['GET', 'POST'])
def add_product_description():
    """Add new product - Step 2: Description"""
    if request.method == 'POST':
        from flask import session
        if 'product_data' not in session:
            session['product_data'] = {}
        session['product_data'].update(request.form.to_dict())
        session.modified = True
        return redirect(url_for('seller.add_product_stocks'))
    return render_template('seller/add_product_description.html')


@seller_bp.route('/add_product_stocks', methods=['GET', 'POST'])
def add_product_stocks():
    """Add new product - Step 3: Stock Information"""
    if request.method == 'POST':
        from flask import session
        if 'product_data' not in session:
            session['product_data'] = {}
        session['product_data'].update(request.form.to_dict())
        session.modified = True
        return redirect(url_for('seller.add_product_preview'))
    return render_template('seller/add_product_stocks.html')


@seller_bp.route('/add_product_preview', methods=['GET', 'POST'])
def add_product_preview():
    """Add new product - Step 4: Preview and Submit"""
    from flask import session
    
    if request.method == 'POST':
        # Get product data from session
        product_data = session.get('product_data', {})
        
        # TODO: Save to database here
        # For now, just clear session and redirect
        session.pop('product_data', None)
        flash('Product added successfully!', 'success')
        return redirect(url_for('seller.seller_products'))
    
    # Get product data for preview
    product_data = session.get('product_data', {})
    return render_template('seller/add_product_preview.html', product_data=product_data)


@seller_bp.route('/dashboard')
def dashboard():
    """Seller dashboard overview"""
    return render_template(
        'seller/dashboard.html',
        active_page='dashboard'
    )


@seller_bp.route('/orders')
def orders():
    """Seller orders management"""
    return render_template(
        'seller/orders.html',
        active_page='orders'
    )


@seller_bp.route('/profile')
def profile():
    """Seller profile management"""
    seller = Seller.query.filter_by(user_id=current_user.id).first()
    return render_template(
        'seller/profile.html',
        active_page='profile',
        seller=seller
    )
