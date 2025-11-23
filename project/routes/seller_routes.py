"""
Seller routes for managing products, orders, and seller dashboard
"""
from decimal import Decimal, InvalidOperation

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    jsonify,
    session,
    current_app,
)
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError

from project import db
from project.models import Product, Seller, User

seller_bp = Blueprint('seller', __name__, url_prefix='/seller')

PLACEHOLDER_IMAGE = '/static/image/banner.png'

CATEGORY_TREE = {
    'Clothing': ['Tops', 'Bottoms', 'Dresses', 'Outerwear', 'Activewear', 'Sleepwear', 'Undergarments', 'Swimwear', 'Occasionwear'],
    'Footwear': ['Heels', 'Flats', 'Sandals', 'Sneakers', 'Boots', 'Slippers & Comfort Wear', 'Occasion / Dress Shoes'],
    'Accessories': ['Bags', 'Jewelry', 'Hair Accessories', 'Belts', 'Scarves & Wraps', 'Hats & Caps', 'Eyewear', 'Watches', 'Gloves', 'Others'],
}


def _to_decimal(raw_value, default='0.00'):
    """Safely convert arbitrary user input to Decimal."""
    if raw_value in (None, ''):
        return Decimal(default)
    try:
        return Decimal(str(raw_value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal(default)


def _to_int(raw_value, default=0):
    """Safely convert to integer."""
    try:
        return int(raw_value)
    except (TypeError, ValueError):
        return default


def _to_bool(raw_value):
    """Convert checkbox style inputs to boolean."""
    if raw_value is None:
        return False
    if isinstance(raw_value, bool):
        return raw_value
    return str(raw_value).lower() in {'true', '1', 'on', 'yes'}


def _split_csv(raw_value):
    if not raw_value:
        return []
    if isinstance(raw_value, (list, tuple)):
        return [item for item in raw_value if item]
    return [chunk.strip() for chunk in str(raw_value).split(',') if chunk.strip()]


def _get_form_value(multi_dict, *keys):
    """Return the first matching value for any of the provided keys."""
    for key in keys:
        if key in multi_dict:
            value = multi_dict.get(key)
            if value:
                return value
    return None


@seller_bp.before_request
@login_required
def restrict_to_seller():
    """Ensure only sellers can access seller routes"""
    if not current_user.is_authenticated:
        flash("Please log in to access seller dashboard.", 'warning')
        return redirect(url_for('auth.login'))
    
    if (getattr(current_user, 'role', '') or '').lower() != 'seller':
        flash("Seller access required.", 'danger')
        return redirect(url_for('main.profile'))
    
    if getattr(current_user, 'is_suspended', False):
        flash("Your seller account is suspended.", 'danger')
        return redirect(url_for('main.index'))


@seller_bp.route('/products')
def seller_products():
    """Seller product management page"""
    seller_products = Product.query.filter_by(
        seller_id=current_user.id
    ).order_by(Product.created_at.desc()).all()

    product_payload = [product.to_dashboard_dict() for product in seller_products]

    return render_template(
        'seller/seller_product_management.html', 
        active_page='products',
        products=seller_products,
        categories=CATEGORY_TREE,
        product_payload=product_payload
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
    if request.method == 'POST':
        product_name = (request.form.get('productName') or '').strip()
        category = (request.form.get('category') or '').strip()
        if not product_name or not category:
            flash('Product name and category are required to publish a product.', 'danger')
            return redirect(url_for('seller.add_product'))

        base_price = _to_decimal(request.form.get('price'))
        discount_type = (request.form.get('discountType') or '').strip().lower() or None
        discount_value = _to_decimal(request.form.get('discountPercentage'))
        sale_price = base_price
        compare_price = None

        if discount_type == 'percentage' and discount_value > 0:
            compare_price = base_price
            percentage_left = max(Decimal('0'), Decimal('100') - discount_value)
            sale_price = (base_price * percentage_left) / Decimal('100')
        elif discount_type == 'fixed' and discount_value > 0:
            compare_price = base_price
            sale_price = max(base_price - discount_value, Decimal('0.00'))

        product = Product(
            seller_id=current_user.id,
            name=product_name,
            description=request.form.get('description') or '',
            category=category,
            subcategory=request.form.get('subcategory') or None,
            price=sale_price,
            compare_at_price=compare_price,
            discount_type=discount_type,
            discount_value=discount_value if discount_value > 0 else None,
            voucher_type=request.form.get('voucherType') or None,
            materials=request.form.get('materials') or '',
            details_fit=request.form.get('detailsFit') or '',
            model_height=request.form.get('modelHeight') or '',
            wearing_size=request.form.get('wearingSize') or '',
            sku=request.form.get('sku') or None,
            barcode=request.form.get('barcode') or None,
            stock=max(_to_int(request.form.get('totalStock')), 0),
            allow_backorder=_to_bool(request.form.get('allowBackorder')),
            track_inventory=_to_bool(request.form.get('trackInventory', True)),
            low_stock_threshold=max(_to_int(request.form.get('lowStockThreshold')), 0),
            attributes={
                'size_guide': _split_csv(_get_form_value(request.form, 'sizeGuide[]', 'sizeGuide')),
                'certifications': _split_csv(_get_form_value(request.form, 'certifications[]', 'certifications')),
                'sub_items': _split_csv(_get_form_value(request.form, 'subitem[]', 'subitem')),
                'filters': _split_csv(_get_form_value(request.form, 'filters[]', 'filters')),
                'supplier': request.form.get('supplier') or '',
                'lead_time': request.form.get('leadTime') or '',
                'warehouse_location': request.form.get('warehouseLocation') or '',
                'reorder_point': request.form.get('reorderPoint') or '',
                'variants': request.form.get('variants') or '',
            },
            image=request.form.get('primaryImage') or PLACEHOLDER_IMAGE,
            secondary_image=request.form.get('secondaryImage') or None,
        )
        product.sync_status()

        try:
            db.session.add(product)
            db.session.commit()
        except SQLAlchemyError as exc:
            db.session.rollback()
            current_app.logger.error("Failed to save product: %s", exc)
            flash('We could not save your product. Please try again.', 'danger')
            return redirect(url_for('seller.add_product_preview'))

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
