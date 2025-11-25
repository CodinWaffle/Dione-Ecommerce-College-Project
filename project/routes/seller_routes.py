"""
Enhanced Seller Routes - Complete Product Workflow
Includes: Form handlers, database integration, preview, and modal details
"""

from decimal import Decimal, InvalidOperation
import json
from datetime import datetime

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
from sqlalchemy import desc

from project import db
from project.models import SellerProduct

seller_bp = Blueprint('seller', __name__, url_prefix='/seller')

PLACEHOLDER_IMAGE = '/static/image/banner.png'

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
    """Split comma-separated values or return list."""
    if not raw_value:
        return []
    if isinstance(raw_value, (list, tuple)):
        return [str(item).strip() for item in raw_value if item]
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


# ============================================================================
# STEP 1: Add Product - Basic Information
# ============================================================================
@seller_bp.route('/add_product', methods=['GET', 'POST'])
def add_product():
    """Add new product - Step 1: Basic Information
    
    Collects:
    - productName
    - price
    - discountPercentage
    - discountType
    - voucherType
    - category
    - subcategory
    - subitem (checkboxes)
    - primaryImage
    - secondaryImage
    """
    if request.method == 'POST':
        if 'product_workflow' not in session:
            session['product_workflow'] = {}
        
        # Save Step 1 data
        session['product_workflow']['step1'] = {
            'productName': request.form.get('productName', '').strip(),
            'price': request.form.get('price', ''),
            'discountPercentage': request.form.get('discountPercentage', ''),
            'discountType': request.form.get('discountType', ''),
            'voucherType': request.form.get('voucherType', ''),
            'category': request.form.get('category', ''),
            'subcategory': request.form.get('subcategory', ''),
            'subitem': request.form.getlist('subitem'),  # Multiple checkboxes
            'primaryImage': request.form.get('primaryImage', ''),
            'secondaryImage': request.form.get('secondaryImage', ''),
        }
        session.modified = True
        
        return redirect(url_for('seller.add_product_description'))
    
    return render_template('seller/add_product.html')


# ============================================================================
# STEP 2: Add Product Description
# ============================================================================
@seller_bp.route('/add_product_description', methods=['GET', 'POST'])
def add_product_description():
    """Add new product - Step 2: Description
    
    Collects:
    - description
    - materials
    - detailsFit
    - sizeGuide[] (file uploads)
    - certifications[] (file uploads)
    """
    if request.method == 'POST':
        if 'product_workflow' not in session:
            session['product_workflow'] = {}
        
        session['product_workflow']['step2'] = {
            'description': request.form.get('description', '').strip(),
            'materials': request.form.get('materials', '').strip(),
            'detailsFit': request.form.get('detailsFit', '').strip(),
            'sizeGuide': request.form.getlist('sizeGuide[]'),
            'certifications': request.form.getlist('certifications[]'),
        }
        session.modified = True
        
        return redirect(url_for('seller.add_product_stocks'))
    
    return render_template('seller/add_product_description.html')


# ============================================================================
# STEP 3: Add Product Stocks
# ============================================================================
@seller_bp.route('/add_product_stocks', methods=['GET', 'POST'])
def add_product_stocks():
    """Add new product - Step 3: Stock Information
    
    Collects variant data:
    - sku_* (SKU for each variant)
    - color_* (Color name)
    - color_picker_* (Color hex value)
    - size_* (Size)
    - variant-stock-input (Stock quantity)
    - lowStockThreshold (Low stock alert level)
    """
    if request.method == 'POST':
        variants = []
        
        # Get all rows from variant table (they will have numbered inputs)
        # Since the HTML uses dynamic names like sku_1, color_1, etc.
        # We need to parse them intelligently
        row_indices = set()
        for key in request.form.keys():
            # Extract row number from keys like 'sku_1', 'color_1', etc.
            parts = key.split('_')
            if len(parts) >= 2 and parts[-1].isdigit():
                row_indices.add(int(parts[-1]))
        
        for idx in sorted(row_indices):
            variant_data = {
                'sku': request.form.get(f'sku_{idx}', '').strip(),
                'color': request.form.get(f'color_{idx}', '').strip(),
                'colorHex': request.form.get(f'color_picker_{idx}', '#000000'),
                'size': request.form.get(f'size_{idx}', '').strip(),
                'stock': _to_int(request.form.get(f'stock_{idx}'), 0),
                'lowStock': _to_int(request.form.get(f'lowStock_{idx}'), 0),
            }
            # Only add if at least one field is filled
            if any([variant_data['sku'], variant_data['color'], variant_data['size']]):
                variants.append(variant_data)
        
        # Calculate total stock
        total_stock = sum(v['stock'] for v in variants)
        
        if 'product_workflow' not in session:
            session['product_workflow'] = {}
        
        session['product_workflow']['step3'] = {
            'variants': variants,
            'totalStock': total_stock,
        }
        session.modified = True
        
        return redirect(url_for('seller.add_product_preview'))
    
    return render_template('seller/add_product_stocks.html')


# ============================================================================
# STEP 4: Preview and Submit
# ============================================================================
@seller_bp.route('/add_product_preview', methods=['GET', 'POST'])
def add_product_preview():
    """Add new product - Step 4: Preview
    
    Displays all collected data for review.
    On POST: Inserts product into database and clears session.
    """
    if request.method == 'POST':
        # Prefer server-side session workflow, but accept JSON/form payloads
        workflow_data = session.get('product_workflow', {}) or {}

        # If session has no workflow, try to parse JSON payload from client
        if not workflow_data:
            payload = request.get_json(silent=True)
            if payload:
                # Expect payload to contain step1/step2/step3
                workflow_data = {
                    'step1': payload.get('step1', {}),
                    'step2': payload.get('step2', {}),
                    'step3': payload.get('step3', {}),
                }
                # Mirror into session for consistency
                session['product_workflow'] = workflow_data
                session.modified = True
            else:
                # Fallback: try to build from form fields (legacy)
                # Build step1
                s1 = {
                    'productName': request.form.get('productName', '').strip(),
                    'price': request.form.get('price', ''),
                    'discountPercentage': request.form.get('discountPercentage', ''),
                    'discountType': request.form.get('discountType', ''),
                    'voucherType': request.form.get('voucherType', ''),
                    'category': request.form.get('category', ''),
                    'subcategory': request.form.get('subcategory', ''),
                    'subitem': request.form.getlist('subitem') if hasattr(request, 'form') else [],
                    'primaryImage': request.form.get('primaryImage', ''),
                    'secondaryImage': request.form.get('secondaryImage', ''),
                }
                # step2
                s2 = {
                    'description': request.form.get('description', '').strip(),
                    'materials': request.form.get('materials', '').strip(),
                    'detailsFit': request.form.get('detailsFit', '').strip(),
                    'sizeGuide': request.form.getlist('sizeGuide[]') if hasattr(request, 'form') else [],
                    'certifications': request.form.getlist('certifications[]') if hasattr(request, 'form') else [],
                }
                # step3 - try to capture variants from form keys
                variants = []
                row_indices = set()
                for key in request.form.keys():
                    parts = key.split('_')
                    if len(parts) >= 2 and parts[-1].isdigit():
                        row_indices.add(int(parts[-1]))
                for idx in sorted(row_indices):
                    v = {
                        'sku': request.form.get(f'sku_{idx}', '').strip(),
                        'color': request.form.get(f'color_{idx}', '').strip(),
                        'colorHex': request.form.get(f'color_picker_{idx}', '#000000'),
                        'size': request.form.get(f'size_{idx}', '').strip(),
                        'stock': _to_int(request.form.get(f'stock_{idx}'), 0),
                        'lowStock': _to_int(request.form.get(f'lowStock_{idx}'), 0),
                    }
                    if any([v['sku'], v['color'], v['size']]):
                        variants.append(v)
                s3 = {'variants': variants, 'totalStock': sum(v.get('stock', 0) for v in variants)}
                workflow_data = {'step1': s1, 'step2': s2, 'step3': s3}
                session['product_workflow'] = workflow_data
                session.modified = True

        step1 = workflow_data.get('step1', {})
        step2 = workflow_data.get('step2', {})
        step3 = workflow_data.get('step3', {})
        
        # Validate required fields
        product_name = step1.get('productName', '').strip()
        category = step1.get('category', '').strip()
        
        if not product_name or not category:
            flash('Product name and category are required.', 'danger')
            return redirect(url_for('seller.add_product'))
        
        base_price = _to_decimal(step1.get('price'))
        discount_type = (step1.get('discountType') or '').lower() or None
        discount_value = _to_decimal(step1.get('discountPercentage', 0))
        
        sale_price = base_price
        compare_price = None
        
        if discount_type == 'percentage' and discount_value > 0:
            compare_price = base_price
            percentage_left = max(Decimal('0'), Decimal('100') - discount_value)
            sale_price = (base_price * percentage_left) / Decimal('100')
        elif discount_type == 'fixed' and discount_value > 0:
            compare_price = base_price
            sale_price = max(base_price - discount_value, Decimal('0.00'))
        
        try:
            product = SellerProduct(
                seller_id=current_user.id,
                name=product_name,
                description=step2.get('description', ''),
                category=category,
                subcategory=step1.get('subcategory'),
                price=float(sale_price),
                compare_at_price=float(compare_price) if compare_price else None,
                discount_type=discount_type,
                discount_value=float(discount_value) if discount_value > 0 else None,
                voucher_type=step1.get('voucherType'),
                materials=step2.get('materials', ''),
                details_fit=step2.get('detailsFit', ''),
                primary_image=step1.get('primaryImage', PLACEHOLDER_IMAGE),
                secondary_image=step1.get('secondaryImage'),
                total_stock=step3.get('totalStock', 0),
                low_stock_threshold=_to_int(request.form.get('lowStockThreshold'), 0),
                variants=step3.get('variants', []),
                attributes={
                    'subitems': step1.get('subitem', []),
                    'size_guides': step2.get('sizeGuide', []),
                    'certifications': step2.get('certifications', []),
                },
                created_at=datetime.utcnow(),
            )
            
            db.session.add(product)
            db.session.commit()
            
            session.pop('product_workflow', None)
            
            flash('Product added successfully!', 'success')
            return redirect(url_for('seller.seller_products'))
            
        except SQLAlchemyError as exc:
            db.session.rollback()
            current_app.logger.error("Failed to save product: %s", exc)
            flash('Error saving product. Please try again.', 'danger')
            return redirect(url_for('seller.add_product_preview'))
    
    workflow_data = session.get('product_workflow', {})
    
    return render_template(
        'seller/add_product_preview.html',
        product_data=workflow_data
    )


# ============================================================================
# Product Management List
# ============================================================================
@seller_bp.route('/products')
def seller_products():
    """Display seller's products in management table"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    products_query = SellerProduct.query.filter_by(
        seller_id=current_user.id
    ).order_by(desc(SellerProduct.created_at))
    
    pagination = products_query.paginate(page=page, per_page=per_page)
    products = pagination.items
    
    return render_template(
        'seller/seller_product_management.html',
        products=products,
        pagination=pagination,
        active_page='products'
    )


# ============================================================================
# Product Details Modal
# ============================================================================
@seller_bp.route('/product/<int:product_id>/details', methods=['GET'])
def product_details(product_id):
    """Get full product details for modal display
    
    Returns JSON with all product information including:
    - Basic info (name, price, category, etc.)
    - Variants
    - Images
    - Descriptions
    """
    product = SellerProduct.query.filter_by(
        id=product_id,
        seller_id=current_user.id
    ).first_or_404()
    
    # Variants may be stored as a JSON string or as a Python list (db.JSON).
    variants = []
    if product.variants:
        try:
            # If it's a string, attempt to decode
            if isinstance(product.variants, str):
                variants = json.loads(product.variants)
            else:
                variants = product.variants
        except Exception:
            variants = []
    
    try:
        if isinstance(product.attributes, str):
            attributes = json.loads(product.attributes)
        else:
            attributes = product.attributes or {}
    except Exception:
        attributes = {}
    
    product_details = {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'category': product.category,
        'subcategory': product.subcategory,
        'price': float(product.price),
        'compare_at_price': float(product.compare_at_price) if product.compare_at_price else None,
        'discount_type': product.discount_type,
        'discount_value': float(product.discount_value) if product.discount_value else None,
        'voucher_type': product.voucher_type,
        'materials': product.materials,
        'details_fit': product.details_fit,
        'primary_image': product.primary_image,
        'secondary_image': product.secondary_image,
        'total_stock': product.total_stock,
        'low_stock_threshold': product.low_stock_threshold,
        'variants': variants,
        'attributes': attributes,
        'created_at': product.created_at.isoformat() if product.created_at else None,
    }
    
    return jsonify(product_details)


@seller_bp.route('/product/<int:product_id>/update', methods=['POST'])
def product_update(product_id):
    """Update product details from seller dashboard modal (expects JSON payload)."""
    product = SellerProduct.query.filter_by(
        id=product_id,
        seller_id=current_user.id
    ).first_or_404()

    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({'error': 'Invalid payload'}), 400

    # Apply allowed updates
    name = payload.get('name')
    description = payload.get('description')
    category = payload.get('category')
    subcategory = payload.get('subcategory')
    price = payload.get('price')
    total_stock = payload.get('total_stock')
    variants = payload.get('variants')
    attributes = payload.get('attributes')
    primary_image = payload.get('primary_image')

    try:
        if name is not None:
            product.name = str(name).strip()
        if description is not None:
            product.description = str(description)
        if category is not None:
            product.category = str(category)
        if subcategory is not None:
            product.subcategory = str(subcategory) if subcategory else None
        if price is not None:
            try:
                product.price = float(price)
            except (TypeError, ValueError):
                pass
        if total_stock is not None:
            try:
                product.total_stock = int(total_stock)
            except (TypeError, ValueError):
                pass
        if variants is not None:
            # Expect variants as list of variant objects. Accept either a
            # Python list or a JSON-serializable structure. Persist as JSON
            # string for compatibility with existing stored rows.
            try:
                # ensure we have a serializable list
                if isinstance(variants, str):
                    # client may have sent a JSON string
                    parsed = json.loads(variants)
                else:
                    parsed = variants
            except Exception:
                parsed = []
            # store as a JSON-serializable Python object (SQLAlchemy JSON column)
            product.variants = parsed
            # Recompute total_stock from variants (sum sizeStocks if present)
            try:
                total = 0
                for v in parsed:
                    if isinstance(v, dict) and v.get('sizeStocks') and isinstance(v.get('sizeStocks'), list):
                        for ss in v.get('sizeStocks'):
                            try:
                                total += int(ss.get('stock', 0))
                            except Exception:
                                continue
                    else:
                        try:
                            total += int(v.get('stock', 0) if isinstance(v, dict) else 0)
                        except Exception:
                            continue
                product.total_stock = int(total)
            except Exception:
                # ignore failures and leave provided total_stock handling below
                pass
        if attributes is not None:
            # attributes may already be a dict/object; store directly
            product.attributes = attributes
        if primary_image is not None:
            product.primary_image = primary_image

        db.session.add(product)
        db.session.commit()

        return jsonify({'success': True, 'product': product.to_dict()})
    except SQLAlchemyError as exc:
        db.session.rollback()
        current_app.logger.error('Failed to update product: %s', exc)
        return jsonify({'error': 'Failed to update'}), 500


@seller_bp.route('/dashboard')
def dashboard():
    """Seller dashboard overview"""
    return render_template(
        'seller/seller_dashboard.html',
        active_page='dashboard'
    )


@seller_bp.route('/orders')
def orders():
    """Seller orders management"""
    return render_template(
        'seller/seller_order_management.html',
        active_page='orders'
    )


@seller_bp.route('/revenue')
def revenue():
    """Seller revenue analytics"""
    return render_template(
        'seller/seller_revenue_analytics.html',
        active_page='revenue'
    )


@seller_bp.route('/customers')
def customers():
    """Seller customer management"""
    return render_template(
        'seller/seller_customer_management.html',
        active_page='customers'
    )


@seller_bp.route('/reviews')
def reviews():
    """Seller reviews and ratings"""
    return render_template(
        'seller/seller_reviews.html',
        active_page='reviews'
    )


@seller_bp.route('/inventory')
def inventory():
    """Seller inventory"""
    return render_template(
        'seller/seller_inventory.html',
        active_page='inventory'
    )


@seller_bp.route('/payment-methods')
def payment_methods():
    """Seller payment methods"""
    return render_template(
        'seller/seller_payment_methods.html',
        active_page='payment-methods'
    )


@seller_bp.route('/profile')
def profile():
    """Seller profile"""
    return render_template(
        'seller/seller_profile.html',
        active_page='profile'
    )


@seller_bp.route('/settings')
def settings():
    """Seller settings"""
    return render_template(
        'seller/seller_settings.html',
        active_page='settings'
    )


@seller_bp.route('/payouts')
def payouts():
    """Seller payouts / earnings"""
    return render_template(
        'seller/seller_payout.html',
        active_page='payouts'
    )
