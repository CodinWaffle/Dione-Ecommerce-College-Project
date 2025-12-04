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
from sqlalchemy import desc, func, or_
from sqlalchemy.orm import joinedload

from project import db
from project.models import (
    SellerProduct,
    ProductVariant,
    VariantSize,
    Order,
    PickupRequest,
    PickupRequestItem,
    User,
    Rider,
)
from project.services.inventory_service import ensure_order_inventory_deducted

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


def _load_variants(variant_payload):
    """Normalize variants field from DB (JSON/Text/None) to list of dicts."""
    if not variant_payload:
        return []
    try:
        if isinstance(variant_payload, str):
            parsed = json.loads(variant_payload)
        else:
            parsed = variant_payload
        return parsed if isinstance(parsed, list) else []
    except Exception:
        return []


def _recalculate_total_stock(variants):
    total = 0
    if not isinstance(variants, list):
        return total
    for variant in variants:
        if not isinstance(variant, dict):
            continue
        size_stocks = variant.get('sizeStocks')
        if isinstance(size_stocks, list) and size_stocks:
            for ss in size_stocks:
                try:
                    total += int(ss.get('stock', 0))
                except Exception:
                    continue
        else:
            try:
                total += int(variant.get('stock', 0))
            except Exception:
                continue
    return max(total, 0)


def _sync_product_variants(product, variant_payload):
    """Persist variants + sizes from JSON payload into normalized tables."""
    variants_list = _load_variants(variant_payload)

    # Remove existing variants to ensure clean sync
    ProductVariant.query.filter_by(product_id=product.id).delete(synchronize_session=False)
    db.session.flush()

    if not variants_list:
        return

    for variant in variants_list:
        if not isinstance(variant, dict):
            continue
        color = (
            variant.get('color')
            or variant.get('variant_name')
            or variant.get('colorName')
        )
        if not color:
            continue

        variant_images = None
        if isinstance(variant.get('images'), (list, tuple)):
            variant_images = variant.get('images')
        elif variant.get('photo'):
            variant_images = [variant.get('photo')]

        pv = ProductVariant(
            product_id=product.id,
            variant_name=str(color),
            variant_sku=variant.get('sku') or variant.get('variant_sku'),
            images_json=variant_images,
        )
        db.session.add(pv)
        db.session.flush()

        size_entries = []
        size_stocks = variant.get('sizeStocks')
        if isinstance(size_stocks, list) and size_stocks:
            size_entries = size_stocks
        elif variant.get('size'):
            size_entries = [{
                'size': variant.get('size'),
                'stock': variant.get('stock', 0),
                'sku': variant.get('sku')
            }]

        for size_entry in size_entries:
            if not isinstance(size_entry, dict):
                continue
            size_label = size_entry.get('size') or size_entry.get('size_label')
            if not size_label:
                continue
            stock_value = _to_int(size_entry.get('stock', 0), 0)
            sku_value = size_entry.get('sku') or None

            vs = VariantSize(
                variant_id=pv.id,
                size_label=str(size_label),
                stock_quantity=stock_value,
                sku=sku_value,
            )
            db.session.add(vs)

STATUS_BUCKET_MAP = {
    'pending': 'pending_orders',
    'confirmed': 'pending_orders',
    'shipping': 'shipped_orders',
    'in_transit': 'in_transit_orders',
    'to_receive_today': 'in_transit_orders',
    'cancelled': 'cancelled_orders',
    'delivered': 'completed_orders',
    'completed': 'completed_orders',
}

STATUS_LABELS = {
    'pending': 'Pending',
    'confirmed': 'Confirmed',
    'shipping': 'To Ship',
    'in_transit': 'In Transit',
    'to_receive_today': 'To Receive Today',
    'delivered': 'Delivered',
    'completed': 'Completed',
    'cancelled': 'Cancelled',
}


def _accumulate_status(stats, status_value, increment=1):
    key = STATUS_BUCKET_MAP.get((status_value or '').lower())
    if key:
        stats[key] += increment


def _status_display_label(status_value):
    normalized = (status_value or '').lower()
    return STATUS_LABELS.get(normalized, (status_value or 'Unknown').replace('_', ' ').title())


def _empty_stats():
    return {
        'total_orders': 0,
        'pending_orders': 0,
        'shipped_orders': 0,
        'in_transit_orders': 0,
        'cancelled_orders': 0,
        'completed_orders': 0,
    }


def _get_order_stats_for_seller(seller_id, orders=None):
    stats = _empty_stats()
    if orders is not None:
        for order in orders:
            _accumulate_status(stats, getattr(order, 'status', None))
        stats['total_orders'] = len(orders)
        return stats

    rows = (
        db.session.query(Order.status, func.count(Order.id))
        .filter(Order.seller_id == seller_id)
        .group_by(Order.status)
        .all()
    )
    total = 0
    for status_value, count in rows:
        total += count
        _accumulate_status(stats, status_value, count)
    stats['total_orders'] = total
    return stats


PICKUP_TERMINAL_STATUSES = {'completed', 'cancelled'}
PICKUP_ACTIVE_STATUSES = {'pending', 'assigned', 'en_route', 'picked_up'}
RIDER_AVAILABLE_STATUSES = {'available', 'on-duty', 'on_duty'}


def _serialize_pickup_request(pickup_request):
    if not pickup_request:
        return None
    rider_user = getattr(pickup_request, 'rider_user', None)
    rider_name = None
    rider_phone = None
    if rider_user:
        rider_name = getattr(rider_user, 'username', None) or getattr(rider_user, 'email', None)
        rider_profiles = getattr(rider_user, 'rider_profile', None)
        rider_profile = None
        if rider_profiles:
            try:
                rider_profile = rider_profiles[0]
            except (TypeError, AttributeError, IndexError):
                rider_profile = rider_profiles
        if rider_profile and getattr(rider_profile, 'phone', None):
            rider_phone = rider_profile.phone
    return {
        'id': pickup_request.id,
        'request_number': pickup_request.request_number,
        'status': pickup_request.status,
        'priority': pickup_request.priority,
        'bulk_order_count': pickup_request.bulk_order_count,
        'pickup_address': pickup_request.pickup_address,
        'pickup_notes': pickup_request.pickup_notes,
        'pickup_contact_name': pickup_request.pickup_contact_name,
        'pickup_contact_phone': pickup_request.pickup_contact_phone,
        'pickup_window_start': pickup_request.pickup_window_start.isoformat() if pickup_request.pickup_window_start else None,
        'pickup_window_end': pickup_request.pickup_window_end.isoformat() if pickup_request.pickup_window_end else None,
        'requested_at': pickup_request.requested_at.isoformat() if pickup_request.requested_at else None,
        'assigned_at': pickup_request.assigned_at.isoformat() if pickup_request.assigned_at else None,
        'picked_up_at': pickup_request.picked_up_at.isoformat() if pickup_request.picked_up_at else None,
        'completed_at': pickup_request.completed_at.isoformat() if pickup_request.completed_at else None,
        'rider_user_id': pickup_request.rider_user_id,
        'rider_name': rider_name,
        'rider_phone': rider_phone,
        'items': [item.to_dict() for item in pickup_request.items],
    }


def _get_active_pickup_item(order):
    pickup_items = getattr(order, 'pickup_items', []) or []
    for item in pickup_items:
        req = getattr(item, 'pickup_request', None)
        if req and (req.status or '').lower() not in PICKUP_TERMINAL_STATUSES:
            return item
    return None


def _parse_iso_datetime(value):
    if not value:
        return None
    try:
        if isinstance(value, datetime):
            return value
        normalized = str(value).replace('Z', '+00:00')
        return datetime.fromisoformat(normalized)
    except Exception:
        return None


def _seller_pickup_defaults(seller_user):
    profile = None
    try:
        profiles = getattr(seller_user, 'seller_profile', None)
        if profiles:
            profile = profiles[0]
    except Exception:
        profile = None

    contact_name = getattr(profile, 'business_name', None) or getattr(seller_user, 'username', None) or seller_user.email
    contact_phone = getattr(profile, 'bank_contact', None) if profile else None
    if not contact_phone:
        contact_phone = getattr(profile, 'phone', None) if profile else None

    address_parts = []
    for attr in ('business_address', 'business_city', 'business_country'):
        if profile:
            value = getattr(profile, attr, None)
            if value:
                address_parts.append(value)
    pickup_address = ', '.join(address_parts) if address_parts else None

    return {
        'contact_name': contact_name,
        'contact_phone': contact_phone,
        'address': pickup_address,
    }


def _build_pickup_request_for_orders(seller_user, orders, payload):
    if not orders:
        raise ValueError('No orders provided for pickup request.')

    defaults = _seller_pickup_defaults(seller_user)
    pickup_address = payload.get('pickup_address') or defaults.get('address')
    pickup_contact_name = payload.get('contact_name') or defaults.get('contact_name')
    pickup_contact_phone = payload.get('contact_phone') or defaults.get('contact_phone')

    pickup_request = PickupRequest(
        seller_id=seller_user.id,
        created_by_id=seller_user.id,
        pickup_address=pickup_address,
        pickup_contact_name=pickup_contact_name,
        pickup_contact_phone=pickup_contact_phone,
        pickup_notes=payload.get('pickup_notes') or payload.get('notes') or '',
        priority=(payload.get('priority') or 'standard').lower(),
        pickup_window_start=_parse_iso_datetime(payload.get('pickup_window_start')),
        pickup_window_end=_parse_iso_datetime(payload.get('pickup_window_end')),
    )

    package_counts = payload.get('package_counts') or {}
    default_package_count = payload.get('package_count')

    for order in orders:
        count_source = package_counts.get(str(order.id)) or package_counts.get(order.id) or default_package_count
        try:
            package_count = int(count_source)
        except Exception:
            package_count = 1
        package_count = max(1, package_count)

        pickup_request.items.append(
            PickupRequestItem(
                order=order,
                seller_id=order.seller_id,
                package_count=package_count,
            )
        )

    pickup_request.bulk_order_count = len(orders)
    db.session.add(pickup_request)
    return pickup_request


def _prepare_order_for_pickup(order):
    now = datetime.utcnow()
    normalized_status = (order.status or '').lower()
    if normalized_status in {'completed', 'cancelled'}:
        raise ValueError('Completed or cancelled orders cannot be scheduled for pickup.')
    if normalized_status not in {'shipping', 'in_transit', 'delivered'}:
        order.status = 'shipping'
    order.updated_at = now
    if not order.shipped_at:
        order.shipped_at = now


def _get_seller_profile_obj(user):
    try:
        profiles = getattr(user, 'seller_profile', None)
        if profiles:
            return profiles[0]
    except Exception:
        return None
    return None


def _normalize_location_value(value):
    if not value:
        return ''
    return str(value).strip().lower()


def _match_rider_location(rider, seller_profile):
    seller_city = _normalize_location_value(getattr(seller_profile, 'business_city', None)) if seller_profile else ''
    seller_country = _normalize_location_value(getattr(seller_profile, 'business_country', None)) if seller_profile else ''
    seller_address = _normalize_location_value(getattr(seller_profile, 'business_address', None)) if seller_profile else ''

    rider_location = _normalize_location_value(getattr(rider, 'current_location', None))
    rider_zones = _normalize_location_value(getattr(rider, 'delivery_zones', None))

    score = 0
    reasons = []

    if seller_city:
        if seller_city and seller_city in rider_location:
            score += 3
            reasons.append('Same city')
        elif seller_city and seller_city in rider_zones:
            score += 2
            reasons.append('Covers seller city')

    if seller_country:
        if seller_country in rider_location or seller_country in rider_zones:
            score += 1
            if 'Same city' not in reasons:
                reasons.append('Same country')

    if not reasons and seller_address and seller_address in rider_location:
        score += 1
        reasons.append('Near address')

    if not reasons:
        reasons.append('Available nearby')

    return score, ', '.join(reasons)


def _get_active_rider_ids():
    rows = (
        db.session.query(PickupRequest.rider_user_id)
        .filter(
            PickupRequest.rider_user_id.isnot(None),
            PickupRequest.status.notin_(list(PICKUP_TERMINAL_STATUSES))
        )
        .distinct()
        .all()
    )
    return {row[0] for row in rows if row[0] is not None}


def _serialize_rider_candidate(rider, score, reason):
    user = getattr(rider, 'user', None)
    display_name = getattr(user, 'username', None) or getattr(user, 'email', None) or f'Rider #{rider.id}'
    return {
        'user_id': rider.user_id,
        'name': display_name,
        'phone': rider.phone,
        'vehicle_type': rider.vehicle_type,
        'current_location': rider.current_location,
        'match_score': score,
        'match_reason': reason,
    }


def _get_eligible_riders_for_seller(seller_user, limit=10):
    seller_profile = _get_seller_profile_obj(seller_user)
    active_rider_ids = _get_active_rider_ids()

    rider_query = (
        Rider.query.join(User, Rider.user_id == User.id)
        .filter(
            User.is_approved.is_(True),
            func.lower(Rider.availability_status).in_(list(RIDER_AVAILABLE_STATUSES)),
        )
        .order_by(Rider.updated_at.desc())
    )

    if active_rider_ids:
        rider_query = rider_query.filter(~Rider.user_id.in_(active_rider_ids))

    riders = rider_query.limit(50).all()
    candidates = []
    for rider in riders:
        score, reason = _match_rider_location(rider, seller_profile)
        candidates.append(_serialize_rider_candidate(rider, score, reason))

    candidates.sort(key=lambda item: (-item['match_score'], item['name'].lower()))
    return candidates[:limit]

def _ensure_mapping(value):
    if isinstance(value, dict):
        return value
    if hasattr(value, 'items'):
        try:
            return dict(value)
        except Exception:
            return {}
    return {}

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
        db.session.flush()

        # Sync normalized variant tables
        _sync_product_variants(product, product.variants)
        
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

                # Ensure expected structure exists
                step1 = json_data.setdefault('step1', {})
                step3 = json_data.setdefault('step3', {})

                # Persist primary/secondary product images if they are base64 strings
                for field, photo_type in (('primaryImage', 'primary'), ('secondaryImage', 'secondary')):
                    photo_data = step1.get(field)
                    if isinstance(photo_data, str) and photo_data.startswith('data:image/'):
                        saved_url = _save_product_photo(photo_data, photo_type)
                        if saved_url:
                            step1[field] = saved_url

                # Persist variant photos if provided as base64 payloads
                variants = step3.get('variants') or []
                processed_variants = []
                for idx, variant in enumerate(variants, start=1):
                    if not isinstance(variant, dict):
                        continue

                    photo_data = variant.get('photo') or variant.get('photoData')
                    if isinstance(photo_data, str) and photo_data.startswith('data:image/'):
                        original_name = variant.get('photoName') or variant.get('sku') or f'variant_{idx}'
                        saved_url = _save_variant_photo(photo_data, original_name, idx)
                        if saved_url:
                            variant['photo'] = saved_url
                    processed_variants.append(variant)

                step3['variants'] = processed_variants

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
    variants = _load_variants(product.variants)
    
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

    # Apply allowed updates - Enhanced for comprehensive edit modal
    name = payload.get('name')
    description = payload.get('description')
    category = payload.get('category')
    subcategory = payload.get('subcategory')
    price = payload.get('price')
    compare_at_price = payload.get('compare_at_price')
    discount_type = payload.get('discount_type')
    discount_value = payload.get('discount_value')
    voucher_type = payload.get('voucher_type')
    materials = payload.get('materials')
    details_fit = payload.get('details_fit')
    status = payload.get('status')
    base_sku = payload.get('base_sku')
    low_stock_threshold = payload.get('low_stock_threshold')
    total_stock = payload.get('total_stock')
    variants = payload.get('variants')
    attributes = payload.get('attributes')
    subitems = payload.get('subitems')
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
                product.price = _to_decimal(price)
            except (TypeError, ValueError):
                pass
        if compare_at_price is not None:
            try:
                product.compare_at_price = _to_decimal(compare_at_price) if compare_at_price else None
            except (TypeError, ValueError):
                pass
        if discount_type is not None:
            product.discount_type = str(discount_type) if discount_type else None
        if discount_value is not None:
            try:
                product.discount_value = _to_decimal(discount_value) if discount_value else None
            except (TypeError, ValueError):
                pass
        if voucher_type is not None:
            product.voucher_type = str(voucher_type) if voucher_type else None
        if materials is not None:
            product.materials = str(materials)
        if details_fit is not None:
            product.details_fit = str(details_fit)
        if status is not None:
            product.status = str(status)
            # Update is_draft based on status
            product.is_draft = (status == 'draft')
        if base_sku is not None:
            product.base_sku = str(base_sku) if base_sku else None
        if low_stock_threshold is not None:
            try:
                product.low_stock_threshold = int(low_stock_threshold)
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
            db.session.flush()
            _sync_product_variants(product, product.variants)
        if attributes is not None:
            if not isinstance(attributes, dict):
                attributes = {}
            product.attributes = attributes
        if subitems is not None:
            try:
                attributes = product.attributes or {}
                attributes['subitems'] = subitems
                product.attributes = attributes
            except Exception:
                pass
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


@seller_bp.route('/product/<int:product_id>/variants', methods=['POST'])
def add_product_variant(product_id):
    """Append a new variant to a product."""
    product = SellerProduct.query.filter_by(
        id=product_id,
        seller_id=current_user.id
    ).first_or_404()

    payload = request.get_json(silent=True) or {}
    try:
        variant = {
            'sku': (payload.get('sku') or '').strip(),
            'color': (payload.get('color') or '').strip(),
            'colorHex': payload.get('colorHex') or payload.get('colorHEX') or '#000000',
            'size': (payload.get('size') or '').strip(),
            'stock': int(payload.get('stock') or 0),
            'lowStock': int(payload.get('lowStock') or 0),
            'photo': payload.get('photo'),
            'sizeStocks': payload.get('sizeStocks') if isinstance(payload.get('sizeStocks'), list) else []
        }

        variants = _load_variants(product.variants)
        variants.append(variant)
        product.variants = variants
        product.total_stock = _recalculate_total_stock(variants)
        db.session.add(product)
        db.session.flush()
        _sync_product_variants(product, product.variants)
        db.session.commit()

        return jsonify({'success': True, 'variants': variants})
    except Exception as exc:
        current_app.logger.error('Failed to add variant: %s', exc)
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to add variant'}), 500


@seller_bp.route('/product/<int:product_id>/variants/<int:variant_index>', methods=['DELETE'])
def delete_product_variant(product_id, variant_index):
    """Remove an existing variant by index."""
    product = SellerProduct.query.filter_by(
        id=product_id,
        seller_id=current_user.id
    ).first_or_404()

    variants = _load_variants(product.variants)
    if variant_index < 0 or variant_index >= len(variants):
        return jsonify({'success': False, 'error': 'Variant not found'}), 404

    try:
        variants.pop(variant_index)
        product.variants = variants
        product.total_stock = _recalculate_total_stock(variants)
        db.session.add(product)
        db.session.flush()
        _sync_product_variants(product, product.variants)
        db.session.commit()
        return jsonify({'success': True, 'variants': variants})
    except Exception as exc:
        current_app.logger.error('Failed to delete variant: %s', exc)
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to delete variant'}), 500


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
    try:
        db_orders = (
            Order.query.filter_by(seller_id=current_user.id)
            .options(
                joinedload(Order.order_items),
                joinedload(Order.pickup_items)
                .joinedload(PickupRequestItem.pickup_request)
                .joinedload(PickupRequest.rider_user)
                .joinedload(User.rider_profile),
            )
            .order_by(Order.created_at.desc())
            .all()
        )
    except Exception as exc:
        current_app.logger.error('Error loading seller orders: %s', exc)
        db_orders = []

    stats = _get_order_stats_for_seller(current_user.id, db_orders)

    return render_template(
        'seller/seller_order_management.html',
        active_page='orders',
        orders=db_orders,
        stats=stats
    )


@seller_bp.route('/orders/<int:order_id>/status', methods=['POST'])
def update_order_status(order_id):
    """Allow sellers to update the status of their orders via AJAX."""
    payload = request.get_json(silent=True) or {}
    new_status = (payload.get('status') or '').strip().lower()
    allowed_statuses = {
        'pending',
        'shipping',
    }

    if new_status not in allowed_statuses:
        return jsonify({'success': False, 'error': 'Invalid status selection.'}), 400

    order = (
        Order.query.filter_by(id=order_id, seller_id=current_user.id)
        .options(joinedload(Order.order_items))
        .first_or_404()
    )
    previous_status = (order.status or '').lower()

    if previous_status == new_status:
        stats = _get_order_stats_for_seller(current_user.id)
        return jsonify({
            'success': True,
            'status': previous_status,
            'status_label': _status_display_label(previous_status),
            'stats': stats,
            'unchanged': True,
            'order_id': order.id,
        })

    now = datetime.utcnow()
    inventory_adjusted = False
    if new_status in {'shipping', 'in_transit'}:
        if not order.shipped_at:
            order.shipped_at = now
        inventory_adjusted = ensure_order_inventory_deducted(order, current_app.logger)
    if new_status in {'delivered', 'completed'}:
        order.delivered_at = now
    if new_status in {'pending', 'confirmed'}:
        # Reset delivery milestones when moving back to earlier stages
        order.shipped_at = None
        order.delivered_at = None

    order.status = new_status
    order.updated_at = now

    try:
        db.session.commit()
    except Exception as exc:
        current_app.logger.error('Failed to update order %s status: %s', order_id, exc)
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Unable to update order status. Please try again.'}), 500

    stats = _get_order_stats_for_seller(current_user.id)

    return jsonify({
        'success': True,
        'status': new_status,
        'status_label': _status_display_label(new_status),
        'order_id': order.id,
        'order_number': order.order_number,
        'updated_at': order.updated_at.isoformat() if order.updated_at else None,
        'shipped_at': order.shipped_at.isoformat() if order.shipped_at else None,
        'delivered_at': order.delivered_at.isoformat() if order.delivered_at else None,
        'stats': stats,
        'inventory_updated': inventory_adjusted,
    })


@seller_bp.route('/orders/<int:order_id>/pickup-summary', methods=['GET'])
@login_required
def get_order_pickup_summary(order_id):
    order = (
        Order.query.filter_by(id=order_id, seller_id=current_user.id)
        .options(
            joinedload(Order.pickup_items)
            .joinedload(PickupRequestItem.pickup_request)
            .joinedload(PickupRequest.rider_user)
            .joinedload(User.rider_profile)
        )
        .first_or_404()
    )
    pickup_item = _get_active_pickup_item(order)
    return jsonify({
        'success': True,
        'pickup': _serialize_pickup_request(pickup_item.pickup_request) if pickup_item else None,
    })


@seller_bp.route('/orders/<int:order_id>/pickup-request', methods=['POST'])
@login_required
def create_pickup_request(order_id):
    payload = request.get_json(silent=True) or {}
    order = (
        Order.query.filter_by(id=order_id, seller_id=current_user.id)
        .options(
            joinedload(Order.pickup_items)
            .joinedload(PickupRequestItem.pickup_request)
            .joinedload(PickupRequest.rider_user)
            .joinedload(User.rider_profile)
        )
        .first_or_404()
    )

    existing_item = _get_active_pickup_item(order)
    if existing_item:
        return jsonify({
            'success': True,
            'pickup': _serialize_pickup_request(existing_item.pickup_request),
            'already_exists': True,
        })

    try:
        _prepare_order_for_pickup(order)
        pickup_request = _build_pickup_request_for_orders(current_user, [order], payload)
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(exc)}), 400
    except Exception as exc:
        current_app.logger.error('Failed to create pickup request for order %s: %s', order_id, exc)
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Unable to create pickup request. Please try again.'}), 500

    return jsonify({
        'success': True,
        'pickup': _serialize_pickup_request(pickup_request),
    }), 201


@seller_bp.route('/orders/pickups/bulk', methods=['POST'])
@login_required
def create_bulk_pickup_request():
    payload = request.get_json(silent=True) or {}
    order_ids = payload.get('order_ids') or []
    if not isinstance(order_ids, (list, tuple)):
        return jsonify({'success': False, 'error': 'order_ids must be an array of order identifiers.'}), 400

    normalized_ids = []
    for raw_id in order_ids:
        try:
            normalized_ids.append(int(raw_id))
        except (ValueError, TypeError):
            continue

    if not normalized_ids:
        return jsonify({'success': False, 'error': 'No valid orders provided for pickup.'}), 400

    orders = (
        Order.query.filter(Order.seller_id == current_user.id, Order.id.in_(normalized_ids))
        .options(
            joinedload(Order.pickup_items)
            .joinedload(PickupRequestItem.pickup_request)
            .joinedload(PickupRequest.rider_user)
            .joinedload(User.rider_profile)
        )
        .all()
    )

    if not orders:
        return jsonify({'success': False, 'error': 'Orders not found or do not belong to you.'}), 404

    conflicts = [order.id for order in orders if _get_active_pickup_item(order)]
    if conflicts:
        return jsonify({
            'success': False,
            'error': 'Some orders already have an active pickup request.',
            'conflicts': conflicts,
        }), 400

    try:
        for order in orders:
            _prepare_order_for_pickup(order)
        pickup_request = _build_pickup_request_for_orders(current_user, orders, payload)
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(exc)}), 400
    except Exception as exc:
        current_app.logger.error('Failed to create bulk pickup request: %s', exc)
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Unable to create pickup request.'}), 500

    return jsonify({
        'success': True,
        'pickup': _serialize_pickup_request(pickup_request),
    }), 201


@seller_bp.route('/pickups/<int:pickup_id>/eligible-riders')
@login_required
def get_eligible_riders_for_pickup(pickup_id):
    PickupRequest.query.filter_by(id=pickup_id, seller_id=current_user.id).first_or_404()
    riders = _get_eligible_riders_for_seller(current_user)
    return jsonify({'success': True, 'riders': riders})


@seller_bp.route('/pickups/<int:pickup_id>/assign', methods=['POST'])
@login_required
def assign_rider_to_pickup(pickup_id):
    return jsonify({
        'success': False,
        'error': 'Manual rider assignment has been disabled. Nearby riders are notified automatically.'
    }), 410


@seller_bp.route('/pickups/<int:pickup_id>/status', methods=['POST'])
@login_required
def update_pickup_status(pickup_id):
    payload = request.get_json(silent=True) or {}
    new_status = (payload.get('status') or '').lower()
    allowed_statuses = {'pending', 'assigned', 'en_route', 'picked_up', 'completed', 'cancelled'}
    if new_status not in allowed_statuses:
        return jsonify({'success': False, 'error': 'Invalid pickup status.'}), 400

    pickup_request = (
        PickupRequest.query.filter_by(id=pickup_id, seller_id=current_user.id)
        .options(
            joinedload(PickupRequest.items).joinedload(PickupRequestItem.order),
            joinedload(PickupRequest.rider_user).joinedload(User.rider_profile),
        )
        .first_or_404()
    )

    pickup_request.mark_status(new_status)
    inventory_updates = []
    if new_status in {'picked_up', 'completed'}:
        for item in pickup_request.items:
            if item.order and ensure_order_inventory_deducted(item.order, current_app.logger):
                inventory_updates.append(item.order_id)
    if new_status == 'cancelled':
        for item in pickup_request.items:
            item.status = 'cancelled'
            item.updated_at = datetime.utcnow()

    try:
        db.session.commit()
    except Exception as exc:
        current_app.logger.error('Failed to update pickup status %s: %s', pickup_id, exc)
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Unable to update pickup status.'}), 500

    return jsonify({
        'success': True,
        'pickup': _serialize_pickup_request(pickup_request),
        'inventory_updates': inventory_updates,
    })


@seller_bp.route('/orders/<int:order_id>/label')
def order_label(order_id):
    """Render a printable shipping label for the seller's order."""
    order = (
        Order.query.filter_by(id=order_id, seller_id=current_user.id)
        .options(joinedload(Order.order_items), joinedload(Order.seller))
        .first_or_404()
    )

    seller_user = order.seller or current_user
    seller_profile = None
    try:
        profiles = getattr(seller_user, 'seller_profile', None)
        if profiles:
            seller_profile = profiles[0]
    except Exception:
        seller_profile = None

    seller_name = ''
    if seller_profile and getattr(seller_profile, 'business_name', None):
        seller_name = seller_profile.business_name
    elif getattr(seller_user, 'username', None):
        seller_name = seller_user.username

    seller_address_parts = [
        getattr(seller_profile, 'business_address', None) if seller_profile else None,
        getattr(seller_profile, 'business_city', None) if seller_profile else None,
        getattr(seller_profile, 'business_country', None) if seller_profile else None,
    ]
    seller_address = ', '.join([part for part in seller_address_parts if part])

    shipping = _ensure_mapping(order.shipping_address or {})
    customer_first = shipping.get('first_name') or shipping.get('firstName')
    customer_last = shipping.get('last_name') or shipping.get('lastName')
    fallback_name = shipping.get('name') or shipping.get('customer_name')
    customer_name = ' '.join(filter(None, [customer_first, customer_last])).strip()
    if not customer_name:
        customer_name = fallback_name or shipping.get('email') or ''

    customer_address_parts = [
        shipping.get('address') or shipping.get('street'),
        shipping.get('apartment') or shipping.get('suite'),
        shipping.get('city'),
        shipping.get('state') or shipping.get('province'),
        shipping.get('zip_code') or shipping.get('zipCode') or shipping.get('zip'),
        shipping.get('country'),
    ]
    customer_address = '\n'.join([part for part in customer_address_parts if part])

    customer_phone = (
        shipping.get('phone')
        or shipping.get('mobile')
        or shipping.get('contact_number')
        or shipping.get('contactNumber')
        or ''
    )

    label_context = {
        'seller': {
            'name': seller_name,
            'address': seller_address,
        },
        'customer': {
            'name': customer_name,
            'address': customer_address,
            'phone': customer_phone,
        },
        'shipping_notes': shipping.get('deliveryNote') or shipping.get('notes') or '',
    }

    return render_template(
        'seller/order_label.html',
        platform_name='DIONE APPAREL',
        order=order,
        seller_info=label_context['seller'],
        customer_info=label_context['customer'],
        shipping_notes=label_context['shipping_notes'],
        shipping_date=order.shipped_at or order.created_at,
        carrier_code=order.tracking_number or '',
        customer_phone=customer_phone,
        generated_at=datetime.utcnow(),
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
