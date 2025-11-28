"""
Enhanced Seller Routes - Complete Product Workflow
Includes: Form handlers, database integration, preview, and modal details
"""

from decimal import Decimal, InvalidOperation
import json
import os
import base64
import uuid
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

def _save_variant_photo(base64_data, original_filename, variant_idx):
    """
    Save a base64 encoded image to the filesystem and return the URL path.
    
    Args:
        base64_data (str): Base64 encoded image data (data:image/jpeg;base64,...)
        original_filename (str): Original filename from the client
        variant_idx (int): Variant index for unique naming
        
    Returns:
        str: URL path to the saved image, or None if failed
    """
    try:
        # Parse the base64 data
        if not base64_data.startswith('data:image/'):
            return None
            
        # Extract the image format and data
        header, data = base64_data.split(',', 1)
        image_format = header.split('/')[1].split(';')[0]  # e.g., 'jpeg', 'png'
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        filename = f"variant_{variant_idx}_{timestamp}_{unique_id}.{image_format}"
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'variants')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(base64.b64decode(data))
        
        # Return the URL path
        return f'/static/uploads/variants/{filename}'
        
    except Exception as e:
        print(f"Error saving variant photo: {e}")
        return None

def _save_product_photo(base64_data, photo_type):
    """
    Save a base64 encoded product image to the filesystem and return the URL path.
    
    Args:
        base64_data (str): Base64 encoded image data (data:image/jpeg;base64,...)
        photo_type (str): 'primary' or 'secondary'
        
    Returns:
        str: URL path to the saved image, or None if failed
    """
    try:
        # Parse the base64 data
        if not base64_data.startswith('data:image/'):
            return None
            
        # Extract the image format and data
        header, data = base64_data.split(',', 1)
        image_format = header.split('/')[1].split(';')[0]  # e.g., 'jpeg', 'png'
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        filename = f"product_{photo_type}_{timestamp}_{unique_id}.{image_format}"
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'products')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(base64.b64decode(data))
        
        # Return the URL path
        return f'/static/uploads/products/{filename}'
        
    except Exception as e:
        print(f"Error saving product photo: {e}")
        return None


@seller_bp.context_processor
def inject_seller_profile():
    """Inject a lightweight `seller` dict into seller templates.

    This makes `seller.business_name`, `seller.business_address` etc available
    in `_header_seller.html` and sidebar partials without passing explicitly
    from every route.
    """
    try:
        if current_user and getattr(current_user, 'is_authenticated', False):
            # current_user may have a backref `seller_profile` (list); take first
            sp_list = getattr(current_user, 'seller_profile', None)
            if sp_list:
                sp = sp_list[0]
                return {
                    'seller': {
                        'business_name': getattr(sp, 'business_name', None),
                        'business_address': getattr(sp, 'business_address', None),
                        'business_city': getattr(sp, 'business_city', None),
                        'business_country': getattr(sp, 'business_country', None),
                        'is_verified': getattr(sp, 'is_verified', False),
                        'logo_url': getattr(sp, 'logo_url', None) or None,
                    }
                }
    except Exception:
        pass
    return {'seller': None}

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


def _save_product_draft(workflow_data):
    """Save product as draft and return product_id"""
    try:
        current_app.logger.info(f"Starting _save_product_draft with data: {workflow_data}")
        
        step1 = workflow_data.get('step1', {})
        step2 = workflow_data.get('step2', {})
        step3 = workflow_data.get('step3', {})
        
        current_app.logger.info(f"Step1 data: {step1}")
        current_app.logger.info(f"Step2 data: {step2}")
        current_app.logger.info(f"Step3 data: {step3}")
        
        # Validate required fields more strictly
        product_name = step1.get('productName', '').strip()
        category = step1.get('category', '').strip()
        
        current_app.logger.info(f"Product name: '{product_name}', Category: '{category}'")
        
        # Reject hardcoded fallback values
        if not product_name or not category:
            raise ValueError(f'Missing required fields: productName="{product_name}", category="{category}"')
        
        # Reject common fallback values that indicate missing user input
        if product_name in ['Premium T-Shirt', 'Test Product', 'Default Product']:
            raise ValueError(f'Invalid product name - appears to be fallback value: "{product_name}"')
        
        if category in ['Fashion'] and not step1.get('subcategory'):
            current_app.logger.warning(f'Generic category "{category}" without subcategory - may be fallback value')
        
        current_app.logger.info(f"Validation passed, current_user.id: {current_user.id}")
        
        # Calculate pricing
        base_price = _to_decimal(step1.get('price'))
        discount_type = (step1.get('discountType') or '').lower() or None
        discount_value = _to_decimal(step1.get('discountPercentage', 0))
        
        current_app.logger.info(f"Pricing calculated - base_price: {base_price}, discount_type: {discount_type}, discount_value: {discount_value}")
        
        sale_price = base_price
        compare_price = None
        
        if discount_type == 'percentage' and discount_value > 0:
            compare_price = base_price
            percentage_left = max(Decimal('0'), Decimal('100') - discount_value)
            sale_price = (base_price * percentage_left) / Decimal('100')
        elif discount_type == 'fixed' and discount_value > 0:
            compare_price = base_price
            sale_price = max(base_price - discount_value, Decimal('0.00'))
        
        current_app.logger.info(f"Final pricing - sale_price: {sale_price}, compare_price: {compare_price}")
        
        # Determine if this is a complete product (all steps finished) or still a draft
        is_complete = (
            bool(product_name and category) and  # Step 1 complete
            bool(step2.get('description')) and   # Step 2 complete  
            bool(step3.get('variants')) and      # Step 3 complete
            step3.get('totalStock', 0) > 0       # Has stock
        )
        
        current_app.logger.info(f"Product completion status: {is_complete}")
        
        # Create or update product
        product = SellerProduct(
            seller_id=current_user.id,
            name=product_name,
            description=step2.get('description', ''),
            category=category,
            subcategory=step1.get('subcategory') or None,
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
            low_stock_threshold=_to_int(step1.get('lowStockThreshold'), 5),
            variants=step3.get('variants', []),
            attributes={
                'subitems': step1.get('subitem', []),
                'size_guides': step2.get('sizeGuide', []),
                'certifications': step2.get('certifications', []),
            },
            draft_data=workflow_data,
            is_draft=not is_complete,  # False if complete, True if still draft
            status='active' if is_complete else 'draft',
            created_at=datetime.utcnow(),
        )
        
        current_app.logger.info(f"Adding product to session...")
        db.session.add(product)
        
        current_app.logger.info(f"Committing to database...")
        db.session.commit()
        
        current_app.logger.info(f"Saved product draft - ID: {product.id}, Name: '{product.name}'")
        return product.id
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to save product draft: {e}")
        raise


@seller_bp.before_request
def restrict_to_seller():
    """Ensure only sellers can access seller routes"""
    if not current_user.is_authenticated:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        flash("Please log in to access seller dashboard.", 'warning')
        return redirect(url_for('auth.login'))
    
    if (getattr(current_user, 'role', '') or '').lower() != 'seller':
        if request.is_json:
            return jsonify({'success': False, 'message': 'Seller access required'}), 403
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
        
        # Process photo uploads
        primary_image_url = None
        secondary_image_url = None
        
        # Handle primary image
        primary_image_data = request.form.get('primaryImage', '')
        if primary_image_data and primary_image_data.startswith('data:image/'):
            try:
                primary_image_url = _save_product_photo(primary_image_data, 'primary')
            except Exception as e:
                print(f"Error saving primary image: {e}")
        
        # Handle secondary image
        secondary_image_data = request.form.get('secondaryImage', '')
        if secondary_image_data and secondary_image_data.startswith('data:image/'):
            try:
                secondary_image_url = _save_product_photo(secondary_image_data, 'secondary')
            except Exception as e:
                print(f"Error saving secondary image: {e}")
        
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
            'primaryImage': primary_image_url or '',
            'secondaryImage': secondary_image_url or '',
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
@login_required
def add_product_stocks():
    """Add new product - Step 3: Stock Information
    
    Now saves as draft and returns JSON for frontend navigation
    """
    if request.method == 'POST':
        try:
            # Check if this is a JSON request
            if request.is_json:
                json_data = request.get_json()
                current_app.logger.info(f"Received JSON request: {json_data}")
                
                # Validate JSON data structure
                if not json_data:
                    return jsonify({
                        'success': False,
                        'message': 'No JSON data received'
                    }), 400
                
                # Save as draft and return product_id for navigation
                product_id = _save_product_draft(json_data)
                
                return jsonify({
                    'success': True,
                    'product_id': product_id,
                    'next': f'/seller/products/preview/{product_id}'
                })
            
            # Handle regular form submission
            variants = []
            row_indices = set()
            for key in request.form.keys():
                parts = key.split('_')
                if len(parts) >= 2 and parts[-1].isdigit():
                    row_indices.add(int(parts[-1]))
            
            for idx in sorted(row_indices):
                # Get basic variant info
                sku = request.form.get(f'sku_{idx}', '').strip()
                color = request.form.get(f'color_{idx}', '').strip()
                color_hex = request.form.get(f'color_picker_{idx}', '#000000')
                low_stock = _to_int(request.form.get(f'lowStock_{idx}'), 0)
                
                # Get photo data
                photo_data = request.form.get(f'variant_photo_{idx}', '')
                photo_name = request.form.get(f'variant_photo_name_{idx}', '')
                photo_url = None
                
                # Process photo if provided
                if photo_data and photo_data.startswith('data:image/'):
                    try:
                        photo_url = _save_variant_photo(photo_data, photo_name, idx)
                    except Exception as e:
                        print(f"Error saving photo for variant {idx}: {e}")
                
                # Parse per-size stocks sent as JSON in a hidden input
                size_stocks_raw = request.form.get(f'sizeStocks_{idx}')
                if size_stocks_raw:
                    try:
                        parsed = json.loads(size_stocks_raw)
                        if isinstance(parsed, list) and len(parsed) > 0:
                            variant_data = {
                                'sku': sku,
                                'color': color,
                                'colorHex': color_hex,
                                'sizeStocks': [],
                                'lowStock': low_stock,
                                'photo': photo_url,
                            }
                            
                            for item in parsed:
                                if isinstance(item, dict) and 'size' in item:
                                    variant_data['sizeStocks'].append({
                                        'size': str(item.get('size')),
                                        'stock': _to_int(item.get('stock', 0), 0)
                                    })
                            
                            if variant_data['color'] or len(variant_data['sizeStocks']) > 0:
                                variants.append(variant_data)
                    except Exception:
                        pass
                else:
                    # Fallback for single size entry
                    size = request.form.get(f'size_{idx}', '').strip()
                    stock = _to_int(request.form.get(f'stock_{idx}'), 0)
                    
                    if size:
                        variant_data = {
                            'sku': sku,
                            'color': color,
                            'colorHex': color_hex,
                            'sizeStocks': [{'size': size, 'stock': stock}],
                            'lowStock': low_stock,
                            'photo': photo_url,
                        }
                    else:
                        variant_data = {
                            'sku': sku,
                            'color': color,
                            'colorHex': color_hex,
                            'size': size,
                            'stock': stock,
                            'lowStock': low_stock,
                            'photo': photo_url,
                        }
                    
                    if any([variant_data['sku'], variant_data['color'], variant_data.get('size'), len(variant_data.get('sizeStocks', []))]):
                        variants.append(variant_data)
            
            # Calculate total stock
            total_stock = 0
            for v in variants:
                if 'sizeStocks' in v:
                    total_stock += sum(size_item.get('stock', 0) for size_item in v['sizeStocks'])
                else:
                    total_stock += v.get('stock', 0)
            
            # Prepare data for draft save
            workflow_data = session.get('product_workflow', {})
            workflow_data['step3'] = {
                'variants': variants,
                'totalStock': total_stock,
            }
            
            # Save as draft
            product_id = _save_product_draft(workflow_data)
            
            # Clear session and redirect to preview
            session.pop('product_workflow', None)
            return redirect(url_for('seller.product_preview', product_id=product_id))
            
        except Exception as e:
            current_app.logger.error(f"Error in add_product_stocks: {e}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            
            if request.is_json:
                return jsonify({
                    'success': False, 
                    'message': f'Server error: {str(e)}',
                    'details': str(e)
                }), 500
            else:
                flash(f'Error saving product: {str(e)}', 'danger')
                return redirect(url_for('seller.add_product_stocks'))
    
    return render_template('seller/add_product_stocks.html')


# Debug endpoint to test basic functionality
@seller_bp.route('/debug_test', methods=['POST'])
@login_required
def debug_test():
    """Simple debug endpoint to test JSON submission"""
    try:
        data = request.get_json()
        current_app.logger.info(f"Debug test received: {data}")
        return jsonify({
            'success': True,
            'message': 'Debug test successful',
            'received_data': data,
            'user_id': current_user.id,
            'user_role': getattr(current_user, 'role', 'unknown')
        })
    except Exception as e:
        current_app.logger.error(f"Debug test error: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ============================================================================
# NEW: Product Preview (from draft)
# ============================================================================
@seller_bp.route('/products/preview/<int:product_id>')
def product_preview(product_id):
    """Preview a draft product before committing"""
    product = SellerProduct.query.filter_by(
        id=product_id,
        seller_id=current_user.id,
        is_draft=True
    ).first_or_404()
    
    return render_template(
        'seller/product_preview.html',
        product=product
    )


@seller_bp.route('/products/<int:product_id>/commit', methods=['POST'])
def commit_product(product_id):
    """Commit a draft product to active status"""
    try:
        product = SellerProduct.query.filter_by(
            id=product_id,
            seller_id=current_user.id,
            is_draft=True
        ).first_or_404()
        
        # Commit the draft
        product.commit_draft()
        db.session.commit()
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Product published successfully!',
                'redirect': url_for('seller.seller_products')
            })
        else:
            flash('Product published successfully!', 'success')
            return redirect(url_for('seller.seller_products'))
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to commit product: {e}")
        
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 500
        else:
            flash('Error publishing product. Please try again.', 'danger')
            return redirect(url_for('seller.product_preview', product_id=product_id))


# ============================================================================
# LEGACY: Keep old preview route for backward compatibility
# ============================================================================
@seller_bp.route('/add_product_preview', methods=['GET', 'POST'])
def add_product_preview():
    """Legacy preview route - redirects to new flow"""
    if request.method == 'POST':
        # Handle legacy POST requests by saving as draft first
        try:
            workflow_data = session.get('product_workflow', {})
            if not workflow_data:
                flash('No product data found. Please start over.', 'warning')
                return redirect(url_for('seller.add_product'))
            
            product_id = _save_product_draft(workflow_data)
            session.pop('product_workflow', None)
            
            if request.is_json:
                return jsonify({
                    'success': True,
                    'product_id': product_id,
                    'redirect': url_for('seller.product_preview', product_id=product_id)
                })
            else:
                return redirect(url_for('seller.product_preview', product_id=product_id))
                
        except Exception as e:
            current_app.logger.error(f"Error in legacy preview: {e}")
            if request.is_json:
                return jsonify({'success': False, 'error': str(e)}), 500
            else:
                flash('Error saving product. Please try again.', 'danger')
                return redirect(url_for('seller.add_product_stocks'))
    
    # GET request - show preview from session data
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
    status_filter = request.args.get('status', 'all')
    
    # Base query
    products_query = SellerProduct.query.filter_by(seller_id=current_user.id)
    
    # Apply status filter
    if status_filter == 'draft':
        products_query = products_query.filter_by(is_draft=True)
    elif status_filter == 'active':
        products_query = products_query.filter_by(is_draft=False, status='active')
    elif status_filter != 'all':
        products_query = products_query.filter_by(status=status_filter)
    
    products_query = products_query.order_by(desc(SellerProduct.created_at))
    
    pagination = products_query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items
    
    # Get counts for status tabs
    total_count = SellerProduct.query.filter_by(seller_id=current_user.id).count()
    draft_count = SellerProduct.query.filter_by(seller_id=current_user.id, is_draft=True).count()
    active_count = SellerProduct.query.filter_by(seller_id=current_user.id, is_draft=False, status='active').count()
    
    return render_template(
        'seller/seller_product_management.html',
        products=products,
        pagination=pagination,
        active_page='products',
        status_filter=status_filter,
        counts={
            'total': total_count,
            'draft': draft_count,
            'active': active_count
        }
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
    secondary_image = payload.get('secondary_image')

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
        if secondary_image is not None:
            product.secondary_image = secondary_image

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
    # Inventory page removed — route deprecated and sidebar entry removed.
    # If needed in future, reintroduce with appropriate template and handlers.
    return redirect(url_for('seller.dashboard'))


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


@seller_bp.route('/debug/check_recent_products')
def debug_check_recent_products():
    """Debug route to check recent products in database"""
    try:
        # Get recent products from database
        products = SellerProduct.query.order_by(desc(SellerProduct.id)).limit(5).all()
        
        result = []
        for product in products:
            product_data = {
                'id': product.id,
                'seller_id': product.seller_id,
                'base_sku': product.base_sku,
                'is_draft': product.is_draft,
                'created_at': product.created_at.isoformat() if product.created_at else None,
                'draft_data_preview': None
            }
            
            # Parse draft_data if available
            if product.draft_data:
                try:
                    draft_data = json.loads(product.draft_data)
                    step1 = draft_data.get('step1', {})
                    step3 = draft_data.get('step3', {})
                    
                    product_data['draft_data_preview'] = {
                        'product_name': step1.get('productName'),
                        'category': step1.get('category'), 
                        'price': step1.get('price'),
                        'variant_count': len(step3.get('variants', [])),
                        'total_stock': step3.get('totalStock', 0)
                    }
                except json.JSONDecodeError:
                    product_data['draft_data_preview'] = 'Invalid JSON'
            
            result.append(product_data)
        
        return jsonify({
            'success': True,
            'count': len(result),
            'products': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@seller_bp.route('/product/<int:product_id>/delete', methods=['DELETE'])
@login_required
def delete_product(product_id):
    """Delete a product from the database"""
    try:
        # Find the product belonging to the current seller
        product = SellerProduct.query.filter_by(
            id=product_id,
            seller_id=current_user.id
        ).first()
        
        if not product:
            return jsonify({
                'success': False,
                'message': 'Product not found or you do not have permission to delete it'
            }), 404
        
        # Store product name for response
        product_name = product.name
        
        # Delete the product
        db.session.delete(product)
        db.session.commit()
        
        current_app.logger.info(f"Product '{product_name}' (ID: {product_id}) deleted by seller {current_user.id}")
        
        return jsonify({
            'success': True,
            'message': f'Product "{product_name}" has been deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to delete product {product_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while deleting the product'
        }), 500


@seller_bp.route('/test')
def test_page():
    """Serve the test page"""
    import os
    test_file_path = os.path.join(current_app.root_path, '..', 'test_page.html')
    with open(test_file_path, 'r', encoding='utf-8') as f:
        return f.read()
