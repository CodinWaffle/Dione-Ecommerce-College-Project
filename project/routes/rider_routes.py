from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from sqlalchemy import or_, func
from datetime import datetime
from decimal import Decimal, InvalidOperation
from werkzeug.utils import secure_filename
import os
import uuid

from ..models import Rider, User, PickupRequest, PickupRequestItem, Order, RiderPayoutRequest
from .. import db
from project.services.auth_service import AuthService

rider_bp = Blueprint('rider', __name__)


def _ensure_rider_access():
    if (getattr(current_user, 'role', '') or '').lower() != 'rider' or not getattr(current_user, 'is_approved', False):
        flash("You don't have access to the rider area.", 'warning')
        return False
    return True


def _get_seller_profile(user_obj):
    """Return the first seller profile associated with the given user."""
    if not user_obj:
        return None
    profile = getattr(user_obj, 'seller_profile', None)
    if profile is None:
        return None
    try:
        return profile[0]
    except (TypeError, AttributeError, IndexError):
        return profile


def _resolve_pickup_contact_number(pickup_request):
    """Ensure riders always see a contact number even if the pickup lacks one."""
    if not pickup_request:
        return None
    if pickup_request.pickup_contact_phone:
        return pickup_request.pickup_contact_phone

    seller_user = getattr(pickup_request, 'seller', None)
    profile = _get_seller_profile(seller_user)
    candidate_fields = (
        'business_phone',
        'contact_phone',
        'phone',
        'bank_contact',
    )
    for field in candidate_fields:
        if profile:
            value = getattr(profile, field, None)
            if value:
                return value

    fallback_fields = ('phone', 'contact_number')
    for field in fallback_fields:
        value = getattr(seller_user, field, None)
        if value:
            return value
    return None


def _collect_pickup_item_names(pickup_request):
    """Return a flat list of product names tied to the pickup request."""
    item_names = []
    if not pickup_request:
        return item_names

    for pickup_item in getattr(pickup_request, 'items', []) or []:
        order = getattr(pickup_item, 'order', None)
        if order and getattr(order, 'order_items', None):
            for order_item in order.order_items:
                if getattr(order_item, 'product_name', None):
                    item_names.append(order_item.product_name)
        elif order and getattr(order, 'order_number', None):
            item_names.append(f"Order #{order.order_number}")

    return item_names


def _normalize_shift_choice(value):
    normalized = (value or '').strip().lower()
    valid_values = {option for option, _ in RIDER_SHIFT_OPTIONS}
    if normalized in valid_values:
        return normalized
    if normalized in LEGACY_AVAILABLE_SHIFT_VALUES:
        return RIDER_SHIFT_DEFAULT
    if normalized in LEGACY_OFF_SHIFT_VALUES:
        return 'off_shift'
    return None


def _resolve_rider_shift_value(rider_profile):
    normalized = _normalize_shift_choice(getattr(rider_profile, 'availability_status', None))
    if normalized:
        return normalized
    return RIDER_SHIFT_DEFAULT


def _is_rider_on_shift(rider_profile):
    if not rider_profile:
        return False
    return _resolve_rider_shift_value(rider_profile) in RIDER_ACTIVE_SHIFT_VALUES


def _get_rider_shift_label(rider_profile):
    value = _resolve_rider_shift_value(rider_profile)
    lookup = {option: label for option, label in RIDER_SHIFT_OPTIONS}
    return value, lookup.get(value, value.replace('_', ' ').title())


def _normalize_location_string(value):
    if not value:
        return ''
    return str(value).strip().lower()


def _collect_rider_location_sources(rider_profile):
    sources = []
    if not rider_profile:
        return sources
    for field in (getattr(rider_profile, 'current_location', None), getattr(rider_profile, 'delivery_zones', None)):
        normalized = _normalize_location_string(field)
        if normalized:
            sources.append(normalized)
    return sources


def _location_matches_rider(rider_profile, *targets):
    rider_sources = _collect_rider_location_sources(rider_profile)
    if not rider_sources:
        return True
    normalized_targets = [
        _normalize_location_string(value)
        for value in targets or []
        if _normalize_location_string(value)
    ]
    if not normalized_targets:
        return True
    for target in normalized_targets:
        for source in rider_sources:
            if target in source:
                return True
    return False


def _pickup_location_targets(pickup_request):
    seller_user = getattr(pickup_request, 'seller', None)
    profile = _get_seller_profile(seller_user)
    if not profile:
        return ()
    return (
        getattr(profile, 'business_city', None),
        getattr(profile, 'business_address', None),
        getattr(profile, 'business_country', None),
    )


def _pickup_visible_to_rider(pickup_request, rider_profile):
    if not pickup_request:
        return False
    rider_user_id = getattr(rider_profile, 'user_id', None)
    if pickup_request.rider_user_id and rider_user_id and pickup_request.rider_user_id == rider_user_id:
        return True
    if not _is_rider_on_shift(rider_profile):
        return False
    return _location_matches_rider(rider_profile, *_pickup_location_targets(pickup_request))


def _delivery_location_targets(order):
    shipping = _normalize_shipping_mapping(order)
    return (
        shipping.get('city') or shipping.get('municipality'),
        shipping.get('province') or shipping.get('state'),
        shipping.get('address') or shipping.get('street'),
        shipping.get('country'),
        shipping.get('zip') or shipping.get('zip_code') or shipping.get('zipCode'),
    )


def _delivery_visible_to_rider(delivery_item, rider_profile, scope='available'):
    order = getattr(delivery_item, 'order', None)
    if not order:
        return False
    _, meta = _get_delivery_meta(order)
    assigned_id = meta.get('delivery_rider_id')
    rider_user_id = getattr(rider_profile, 'user_id', None)
    if scope in {'assigned', 'history'}:
        return assigned_id and rider_user_id and assigned_id == rider_user_id
    if not _is_rider_on_shift(rider_profile):
        return False
    if assigned_id and assigned_id != rider_user_id:
        return False
    return _location_matches_rider(rider_profile, *_delivery_location_targets(order))


def _get_rider_profile_obj(user_id=None):
    user_id = user_id or getattr(current_user, 'id', None)
    if not user_id:
        return None
    return Rider.query.filter_by(user_id=user_id).first()


DELIVERY_READY_STATUSES = {'ready_for_delivery', 'delivery_rejected', 'picked_up'}
DELIVERY_ACTIVE_STATUSES = {'delivery_assigned', 'to_receive_today'}
DELIVERY_DONE_STATUSES = {'delivered', 'cancelled'}
DELIVERY_STATUS_LABELS = {
    'ready_for_delivery': 'Ready for Delivery',
    'delivery_rejected': 'Needs Rider',
    'picked_up': 'Awaiting Dispatch',
    'delivery_assigned': 'Assigned',
    'to_receive_today': 'To Receive Today',
    'delivered': 'Delivered',
    'cancelled': 'Cancelled',
}
DELIVERY_PROOF_SUBDIR = os.path.join('static', 'uploads', 'delivery_proofs')
RIDER_DELIVERY_COMMISSION = 100

RIDER_SHIFT_OPTIONS = [
    ('day_shift', 'Day Shift (6 AM – 2 PM)'),
    ('swing_shift', 'Swing Shift (2 PM – 10 PM)'),
    ('night_shift', 'Night Shift (10 PM – 6 AM)'),
    ('off_shift', 'Off Shift / Break'),
]
RIDER_ACTIVE_SHIFT_VALUES = {value for value, _ in RIDER_SHIFT_OPTIONS if value != 'off_shift'}
RIDER_SHIFT_DEFAULT = 'day_shift'
LEGACY_AVAILABLE_SHIFT_VALUES = {'available', 'on-duty', 'on_duty'}
LEGACY_OFF_SHIFT_VALUES = {'off', 'off-duty', 'off_duty'}
PICKUP_EARNING_RATE = Decimal('100')
DELIVERY_EARNING_RATE = Decimal('50')
MONEY_QUANTIZER = Decimal('0.01')
ZERO = Decimal('0')


def _normalize_shipping_mapping(order):
    source = getattr(order, 'shipping_address', None)
    if isinstance(source, dict):
        return dict(source)
    return {}


def _get_delivery_meta(order):
    shipping = _normalize_shipping_mapping(order)
    meta = shipping.get('_delivery_meta')
    if not isinstance(meta, dict):
        meta = {}
    return shipping, meta


def _persist_delivery_meta(order, shipping, meta):
    shipping['_delivery_meta'] = meta
    order.shipping_address = shipping


def _format_shipping_contact(order):
    shipping = _normalize_shipping_mapping(order)
    name_parts = [
        shipping.get('first_name') or shipping.get('firstName'),
        shipping.get('last_name') or shipping.get('lastName'),
    ]
    fallback_name = shipping.get('name') or shipping.get('customer_name')
    full_name = ' '.join([part for part in name_parts if part])
    if not full_name:
        full_name = fallback_name or getattr(order.buyer, 'username', None) or getattr(order.buyer, 'email', None)

    contact_number = shipping.get('phone') or shipping.get('mobile') or shipping.get('contact_number')
    address_parts = [
        shipping.get('address') or shipping.get('street'),
        shipping.get('apartment') or shipping.get('suite'),
        shipping.get('city'),
        shipping.get('state') or shipping.get('province'),
        shipping.get('zip_code') or shipping.get('zipCode') or shipping.get('zip'),
        shipping.get('country'),
    ]
    full_address = ', '.join([part for part in address_parts if part]) or '—'
    payment_method = shipping.get('payment_method') or shipping.get('paymentMethod') or 'COD'

    return full_name or 'Customer', contact_number or 'Not provided', full_address, payment_method


def _decimalize(value):
    if value is None:
        return ZERO
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError):
        return ZERO


def _payout_sum_for_rider(rider_id, statuses):
    if not rider_id:
        return ZERO
    result = (
        db.session.query(func.coalesce(func.sum(RiderPayoutRequest.amount), 0))
        .filter(
            RiderPayoutRequest.rider_id == rider_id,
            RiderPayoutRequest.status.in_(statuses)
        )
        .scalar()
    )
    return _decimalize(result).quantize(MONEY_QUANTIZER)


def _build_rider_earnings_snapshot(rider_profile, rider_user_id):
    pickup_count = PickupRequest.query.filter(
        PickupRequest.rider_user_id == rider_user_id,
        PickupRequest.status == 'completed'
    ).count()

    delivered_count = (
        PickupRequestItem.query
        .join(PickupRequest, PickupRequestItem.pickup_request_id == PickupRequest.id)
        .filter(
            PickupRequestItem.status == 'delivered',
            PickupRequest.rider_user_id == rider_user_id
        )
        .count()
    )

    pickup_amount = (PICKUP_EARNING_RATE * pickup_count).quantize(MONEY_QUANTIZER)
    delivery_amount = (DELIVERY_EARNING_RATE * delivered_count).quantize(MONEY_QUANTIZER)
    total_earned = (pickup_amount + delivery_amount).quantize(MONEY_QUANTIZER)

    rider_id = getattr(rider_profile, 'id', None)
    total_paid = _payout_sum_for_rider(rider_id, ['paid'])
    pending_payout_amount = _payout_sum_for_rider(rider_id, ['pending'])

    available_balance = total_earned - total_paid - pending_payout_amount
    if available_balance < ZERO:
        available_balance = ZERO
    available_balance = available_balance.quantize(MONEY_QUANTIZER)

    last_payout = None
    payout_history = []
    if rider_id:
        last_payout = (
            RiderPayoutRequest.query
            .filter(
                RiderPayoutRequest.rider_id == rider_id,
                RiderPayoutRequest.status == 'paid'
            )
            .order_by(
                RiderPayoutRequest.processed_at.desc(),
                RiderPayoutRequest.requested_at.desc()
            )
            .first()
        )
        payout_history = (
            RiderPayoutRequest.query
            .filter(RiderPayoutRequest.rider_id == rider_id)
            .order_by(RiderPayoutRequest.requested_at.desc())
            .limit(20)
            .all()
        )

    return {
        'pickup_count': pickup_count,
        'delivery_count': delivered_count,
        'pickup_amount': pickup_amount,
        'delivery_amount': delivery_amount,
        'total_earned': total_earned,
        'total_paid': total_paid,
        'pending_payout_amount': pending_payout_amount,
        'available_balance': available_balance,
        'last_payout': last_payout,
        'payout_history': payout_history,
    }


def _serialize_delivery_item(item, active_rider_id=None):
    order = getattr(item, 'order', None)
    pickup_request = getattr(item, 'pickup_request', None)
    if not order:
        return None

    customer_name, contact_number, address, payment_method = _format_shipping_contact(order)
    shipping, meta = _get_delivery_meta(order)
    assigned_rider_id = meta.get('delivery_rider_id')
    proof_url = meta.get('delivery_proof_url') or item.proof_photo_url
    payment_received = bool(meta.get('payment_received'))
    commission_amount = meta.get('commission_amount') or (RIDER_DELIVERY_COMMISSION if meta.get('commission_awarded') else 0)

    status_value = (item.status or '').lower()
    status_label = DELIVERY_STATUS_LABELS.get(status_value, (item.status or 'Unknown').replace('_', ' ').title())
    assigned_to_me = bool(active_rider_id and assigned_rider_id == active_rider_id)

    return {
        'id': item.id,
        'order_id': order.id,
        'order_number': order.order_number,
        'customer_name': customer_name,
        'address': address,
        'contact': contact_number,
        'payment_method': payment_method,
        'status': status_label,
        'raw_status': status_value or 'ready_for_delivery',
        'order_status': order.status,
        'assigned_to_me': assigned_to_me,
        'proof_photo_url': proof_url,
        'payment_received': payment_received,
        'commission_amount': commission_amount,
    }


def _serialize_pickup_for_rider(pickup_request, active_rider_id=None):
    if not pickup_request:
        return None

    seller_name = pickup_request.pickup_contact_name
    if not seller_name and pickup_request.seller:
        seller_name = getattr(pickup_request.seller, 'username', None) or pickup_request.seller.email

    total_items = sum((item.package_count or 1) for item in pickup_request.items) or len(pickup_request.items)
    assigned_to_me = bool(active_rider_id and pickup_request.rider_user_id == active_rider_id)
    item_names = _collect_pickup_item_names(pickup_request)
    item_summary = ', '.join(item_names)
    if not item_summary and total_items:
        label = 'item' if total_items == 1 else 'items'
        item_summary = f"{total_items} {label}"
    contact_number = _resolve_pickup_contact_number(pickup_request)

    return {
        'id': pickup_request.id,
        'pickup_no': pickup_request.request_number,
        'seller_name': seller_name,
        'address': pickup_request.pickup_address,
        'contact': contact_number,
        'items': total_items,
        'item_names': item_names,
        'item_summary': item_summary,
        'notes': pickup_request.pickup_notes,
        'status': (pickup_request.status or '').replace('_', ' ').title(),
        'raw_status': pickup_request.status,
        'order_ids': [item.order_id for item in pickup_request.items],
        'requested_at': pickup_request.requested_at,
        'assigned_to_me': assigned_to_me,
        'rider_user_id': pickup_request.rider_user_id,
    }


def _rider_pickup_queryset(scope, rider_user_id):
    query = PickupRequest.query.options(
        joinedload(PickupRequest.items)
        .joinedload(PickupRequestItem.order)
        .joinedload(Order.order_items)
    )
    scope = (scope or 'available').lower()

    if scope == 'assigned':
        query = query.filter(PickupRequest.rider_user_id == rider_user_id)
    elif scope == 'history':
        query = query.filter(
            PickupRequest.rider_user_id == rider_user_id,
            PickupRequest.status.in_(['picked_up', 'completed', 'cancelled'])
        )
    else:
        query = query.filter(
            PickupRequest.status.in_(['pending', 'assigned']),
            or_(PickupRequest.rider_user_id.is_(None), PickupRequest.rider_user_id == rider_user_id)
        )

    return query.order_by(PickupRequest.requested_at.desc())


def _rider_delivery_queryset(scope, rider_user_id):
    query = (
        PickupRequestItem.query
        .join(PickupRequest, PickupRequestItem.pickup_request_id == PickupRequest.id)
        .join(Order, PickupRequestItem.order_id == Order.id)
        .options(
            joinedload(PickupRequestItem.order).joinedload(Order.order_items),
            joinedload(PickupRequestItem.order).joinedload(Order.buyer),
            joinedload(PickupRequestItem.pickup_request),
        )
    )

    scope = (scope or 'available').lower()
    if scope == 'assigned':
        query = query.filter(PickupRequestItem.status.in_(DELIVERY_ACTIVE_STATUSES))
    elif scope == 'history':
        query = query.filter(PickupRequestItem.status.in_(DELIVERY_DONE_STATUSES))
    else:
        query = query.filter(PickupRequestItem.status.in_(DELIVERY_READY_STATUSES))

    return query.order_by(PickupRequestItem.updated_at.desc())


def _rider_dashboard_counts(rider_user_id):
    pending = PickupRequest.query.filter(
        PickupRequest.status.in_(['pending', 'assigned']),
        or_(PickupRequest.rider_user_id.is_(None), PickupRequest.rider_user_id == rider_user_id)
    ).count()
    completed = PickupRequest.query.filter(
        PickupRequest.rider_user_id == rider_user_id,
        PickupRequest.status == 'completed'
    ).count()
    return pending, completed


@rider_bp.route('/rider/dashboard')
@login_required
def rider_dashboard():
    if not _ensure_rider_access():
        return redirect(url_for('main.profile'))
    pending_pickups, completed_pickups = _rider_dashboard_counts(current_user.id)
    return render_template(
        'rider/rider_dashboard.html',
        username=current_user.email,
        pending_pickups_count=pending_pickups,
        completed_pickups_count=completed_pickups,
    )


@rider_bp.route('/rider/pickup-management')
@login_required
def pickup_management():
    if not _ensure_rider_access():
        return redirect(url_for('main.profile'))
    rider_profile = _get_rider_profile_obj(current_user.id)
    shift_value, shift_label = _get_rider_shift_label(rider_profile)
    on_shift = _is_rider_on_shift(rider_profile)
    pickups = _rider_pickup_queryset('available', current_user.id).limit(25).all()
    pickups = [pickup for pickup in pickups if _pickup_visible_to_rider(pickup, rider_profile)]
    pickup_rows = [_serialize_pickup_for_rider(pickup, current_user.id) for pickup in pickups]
    return render_template(
        'rider/pickup_management.html',
        username=current_user.email,
        pickups=pickup_rows,
        on_shift=on_shift,
        shift_value=shift_value,
        shift_label=shift_label,
    )


@rider_bp.route('/rider/api/pickups')
@login_required
def pickup_list_api():
    if not _ensure_rider_access():
        return jsonify({'success': False, 'error': "You don't have access to pickups."}), 403

    scope = request.args.get('scope', 'available')
    rider_profile = _get_rider_profile_obj(current_user.id)
    shift_value, shift_label = _get_rider_shift_label(rider_profile)
    on_shift = _is_rider_on_shift(rider_profile)
    pickups = _rider_pickup_queryset(scope, current_user.id).all()
    if scope not in {'assigned', 'history'}:
        pickups = [pickup for pickup in pickups if _pickup_visible_to_rider(pickup, rider_profile)]
    return jsonify({
        'success': True,
        'pickups': [_serialize_pickup_for_rider(pickup, current_user.id) for pickup in pickups],
        'on_shift': on_shift,
        'shift_value': shift_value,
        'shift_label': shift_label,
    })


@rider_bp.route('/rider/api/pickups/<int:pickup_id>/accept', methods=['POST'])
@login_required
def pickup_accept_api(pickup_id):
    if not _ensure_rider_access():
        return jsonify({'success': False, 'error': "You don't have access to pickups."}), 403

    rider_profile = _get_rider_profile_obj(current_user.id)
    if not _is_rider_on_shift(rider_profile):
        return jsonify({'success': False, 'error': 'Switch to an active shift to accept pickups.'}), 403

    pickup_request = (
        PickupRequest.query.filter_by(id=pickup_id)
        .options(joinedload(PickupRequest.items))
        .first_or_404()
    )

    rider_profile = _get_rider_profile_obj(current_user.id)
    if not _pickup_visible_to_rider(pickup_request, rider_profile):
        return jsonify({'success': False, 'error': 'This pickup is not available in your coverage area.'}), 403

    if pickup_request.rider_user_id and pickup_request.rider_user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Pickup already assigned to another rider.'}), 400

    if not _pickup_visible_to_rider(pickup_request, rider_profile):
        return jsonify({'success': False, 'error': 'This pickup is outside your coverage area or already assigned.'}), 403

    pickup_request.rider_user_id = current_user.id
    pickup_request.mark_status('assigned')
    pickup_request.assigned_at = datetime.utcnow()

    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Unable to accept pickup.'}), 500

    return jsonify({'success': True, 'pickup': _serialize_pickup_for_rider(pickup_request, current_user.id)})


@rider_bp.route('/rider/api/pickups/<int:pickup_id>/complete', methods=['POST'])
@login_required
def pickup_complete_api(pickup_id):
    if not _ensure_rider_access():
        return jsonify({'success': False, 'error': "You don't have access to pickups."}), 403

    payload = request.get_json(silent=True) or {}
    proof_photo_url = payload.get('proof_photo_url')
    rider_notes = payload.get('rider_notes')
    mark_complete = payload.get('mark_complete', True)

    pickup_request = (
        PickupRequest.query.filter_by(id=pickup_id)
        .options(joinedload(PickupRequest.items).joinedload(PickupRequestItem.order))
        .first_or_404()
    )

    if pickup_request.rider_user_id and pickup_request.rider_user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Pickup is assigned to another rider.'}), 400

    pickup_request.rider_user_id = pickup_request.rider_user_id or current_user.id

    now = datetime.utcnow()
    pickup_request.mark_status('picked_up')
    pickup_request.picked_up_at = now

    for item in pickup_request.items:
        item.status = 'ready_for_delivery'
        if proof_photo_url:
            item.proof_photo_url = proof_photo_url
        if rider_notes:
            item.rider_notes = rider_notes
        item.updated_at = now
        if item.order:
            item.order.status = 'in_transit'
            item.order.updated_at = now
            if not item.order.shipped_at:
                item.order.shipped_at = now
            shipping_meta, delivery_meta = _get_delivery_meta(item.order)
            if 'pickup_completed_at' not in delivery_meta:
                delivery_meta['pickup_completed_at'] = now.isoformat()
            delivery_meta['pickup_completed_by'] = current_user.id
            _persist_delivery_meta(item.order, shipping_meta, delivery_meta)

    if mark_complete:
        pickup_request.mark_status('completed')
        pickup_request.completed_at = now

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Unable to update pickup.'}), 500

    return jsonify({'success': True, 'pickup': _serialize_pickup_for_rider(pickup_request, current_user.id)})


@rider_bp.route('/rider/api/deliveries')
@login_required
def delivery_list_api():
    if not _ensure_rider_access():
        return jsonify({'success': False, 'error': "You don't have access to deliveries."}), 403

    scope = request.args.get('scope', 'available')
    rider_profile = _get_rider_profile_obj(current_user.id)
    shift_value, shift_label = _get_rider_shift_label(rider_profile)
    on_shift = _is_rider_on_shift(rider_profile)
    deliveries = _rider_delivery_queryset(scope, current_user.id).all()
    deliveries = [
        item for item in deliveries
        if _delivery_visible_to_rider(item, rider_profile, scope)
    ]
    payload = [
        item for item in (
            _serialize_delivery_item(delivery, current_user.id)
            for delivery in deliveries
        ) if item
    ]
    return jsonify({
        'success': True,
        'deliveries': payload,
        'on_shift': on_shift,
        'shift_value': shift_value,
        'shift_label': shift_label,
    })


@rider_bp.route('/rider/api/deliveries/<int:item_id>/accept', methods=['POST'])
@login_required
def delivery_accept_api(item_id):
    if not _ensure_rider_access():
        return jsonify({'success': False, 'error': "You don't have access to deliveries."}), 403

    rider_profile = _get_rider_profile_obj(current_user.id)
    if not _is_rider_on_shift(rider_profile):
        return jsonify({'success': False, 'error': 'Switch to an active shift to accept deliveries.'}), 403

    item = (
        PickupRequestItem.query
        .options(joinedload(PickupRequestItem.order), joinedload(PickupRequestItem.pickup_request))
        .filter_by(id=item_id)
        .first_or_404()
    )

    if (item.status or '').lower() not in DELIVERY_READY_STATUSES:
        return jsonify({'success': False, 'error': 'This delivery is no longer available.'}), 400

    pickup_request = item.pickup_request
    if pickup_request and pickup_request.rider_user_id and pickup_request.rider_user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Delivery already assigned to another rider.'}), 400

    pickup_request.rider_user_id = pickup_request.rider_user_id or current_user.id if pickup_request else current_user.id
    item.status = 'delivery_assigned'
    item.updated_at = datetime.utcnow()

    if item.order:
        shipping_meta, delivery_meta = _get_delivery_meta(item.order)
        delivery_meta['delivery_rider_id'] = current_user.id
        delivery_meta['delivery_assigned_at'] = datetime.utcnow().isoformat()
        _persist_delivery_meta(item.order, shipping_meta, delivery_meta)

    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        if not _delivery_visible_to_rider(item, rider_profile, 'available'):
            return jsonify({'success': False, 'error': 'Delivery is not available in your coverage area or has already been claimed.'}), 403

@rider_bp.route('/rider/api/deliveries/<int:item_id>/reject', methods=['POST'])
@login_required
def delivery_reject_api(item_id):
    if not _ensure_rider_access():
        return jsonify({'success': False, 'error': "You don't have access to deliveries."}), 403

    payload = request.get_json(silent=True) or {}
    reason = payload.get('reason')

    item = (
        PickupRequestItem.query
        .options(joinedload(PickupRequestItem.order), joinedload(PickupRequestItem.pickup_request))
        .filter_by(id=item_id)
        .first_or_404()
    )

    normalized_status = (item.status or '').lower()
    if normalized_status not in DELIVERY_READY_STATUSES | DELIVERY_ACTIVE_STATUSES:
        return jsonify({'success': False, 'error': 'Delivery cannot be rejected at this stage.'}), 400

    shipping_meta, delivery_meta = _get_delivery_meta(item.order)
    assigned_id = delivery_meta.get('delivery_rider_id')
    if not assigned_id or assigned_id != current_user.id:
        return jsonify({'success': False, 'error': 'Only the assigned rider can reject this delivery.'}), 403

    item.status = 'delivery_rejected'
    item.updated_at = datetime.utcnow()
    if reason:
        item.rider_notes = (item.rider_notes or '') + f"\nRejected: {reason}"

    delivery_meta.pop('delivery_rider_id', None)
    _persist_delivery_meta(item.order, shipping_meta, delivery_meta)

    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        current_app.logger.error('Failed to reject delivery %s: %s', item_id, exc)
        return jsonify({'success': False, 'error': 'Unable to reject delivery.'}), 500

    return jsonify({'success': True, 'delivery': _serialize_delivery_item(item, current_user.id)})


def _save_delivery_proof(photo):
    if not photo:
        return None
    filename = secure_filename(photo.filename or f"proof-{uuid.uuid4().hex}.jpg")
    if not filename:
        filename = f"proof-{uuid.uuid4().hex}.jpg"
    upload_dir = os.path.join(current_app.root_path, DELIVERY_PROOF_SUBDIR)
    os.makedirs(upload_dir, exist_ok=True)
    name, ext = os.path.splitext(filename)
    if not ext:
        ext = '.jpg'
    filename = f"{name}-{uuid.uuid4().hex[:6]}{ext}"
    save_path = os.path.join(upload_dir, filename)
    photo.save(save_path)
    rel_path = os.path.join('static', 'uploads', 'delivery_proofs', filename).replace('\\', '/')
    return f"/{rel_path}"


def _parse_bool(value):
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {'1', 'true', 'yes', 'on'}


@rider_bp.route('/rider/api/deliveries/<int:item_id>/status', methods=['POST'])
@login_required
def delivery_status_api(item_id):
    if not _ensure_rider_access():
        return jsonify({'success': False, 'error': "You don't have access to deliveries."}), 403

    payload = request.form if request.form else request.get_json(silent=True) or {}
    target_status = (payload.get('status') or '').lower()
    if target_status not in {'to_receive_today', 'delivered'}:
        return jsonify({'success': False, 'error': 'Unsupported status update.'}), 400

    item = (
        PickupRequestItem.query
        .options(joinedload(PickupRequestItem.order), joinedload(PickupRequestItem.pickup_request))
        .filter_by(id=item_id)
        .first_or_404()
    )

    now = datetime.utcnow()
    shipping_meta, delivery_meta = _get_delivery_meta(item.order)
    assigned_id = delivery_meta.get('delivery_rider_id')
    if not assigned_id or assigned_id != current_user.id:
        return jsonify({'success': False, 'error': 'Only the rider assigned to this delivery can update its status.'}), 403

    if target_status == 'to_receive_today':
        item.status = 'to_receive_today'
        item.updated_at = now
        item.order.status = 'to_receive_today'
        item.order.updated_at = now
        delivery_meta['to_receive_today_at'] = now.isoformat()
        _persist_delivery_meta(item.order, shipping_meta, delivery_meta)
    else:
        payment_received = _parse_bool(payload.get('payment_received'))
        proof_photo = request.files.get('photo') if hasattr(request, 'files') else None
        proof_url = payload.get('photo_url')

        if not proof_photo and not proof_url:
            return jsonify({'success': False, 'error': 'Delivery proof photo is required.'}), 400
        if not payment_received:
            return jsonify({'success': False, 'error': 'Payment confirmation is required before completing delivery.'}), 400

        stored_url = proof_url or _save_delivery_proof(proof_photo)
        if not stored_url:
            return jsonify({'success': False, 'error': 'Unable to store delivery proof.'}), 500

        item.status = 'delivered'
        item.proof_photo_url = stored_url
        item.updated_at = now
        item.order.status = 'delivered'
        item.order.delivered_at = now
        item.order.updated_at = now

        delivery_meta['delivery_proof_url'] = stored_url
        delivery_meta['payment_received'] = True
        delivery_meta['payment_received_at'] = now.isoformat()
        delivery_meta['delivery_completed_at'] = now.isoformat()
        delivery_meta['delivery_rider_id'] = current_user.id

        rider_profile = Rider.query.filter_by(user_id=current_user.id).first()
        if rider_profile:
            rider_profile.total_deliveries = (rider_profile.total_deliveries or 0) + 1
            rider_profile.updated_at = now

        if not delivery_meta.get('commission_awarded'):
            delivery_meta['commission_awarded'] = True
            delivery_meta['commission_amount'] = RIDER_DELIVERY_COMMISSION
        _persist_delivery_meta(item.order, shipping_meta, delivery_meta)

    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        current_app.logger.error('Failed to update delivery %s status: %s', item_id, exc)
        return jsonify({'success': False, 'error': 'Unable to update delivery status.'}), 500

    return jsonify({'success': True, 'delivery': _serialize_delivery_item(item, current_user.id)})


@rider_bp.route('/rider/delivery-management')
@login_required
def delivery_management():
    if not _ensure_rider_access():
        return redirect(url_for('main.profile'))
    return redirect(url_for('rider.deliveries'))


@rider_bp.route('/rider/job-list')
@login_required
def job_list():
    if not _ensure_rider_access():
        return redirect(url_for('main.profile'))
    return render_template('rider/job_list.html', username=current_user.email)


@rider_bp.route('/rider/deliveries')
@login_required
def deliveries():
    if not _ensure_rider_access():
        return redirect(url_for('main.profile'))
    rider_profile = _get_rider_profile_obj(current_user.id)
    shift_value, shift_label = _get_rider_shift_label(rider_profile)
    on_shift = _is_rider_on_shift(rider_profile)
    available_items = _rider_delivery_queryset('available', current_user.id).limit(50).all()
    available_items = [item for item in available_items if _delivery_visible_to_rider(item, rider_profile, 'available')]
    assigned_items = _rider_delivery_queryset('assigned', current_user.id).limit(50).all()
    assigned_items = [item for item in assigned_items if _delivery_visible_to_rider(item, rider_profile, 'assigned')]
    seen_ids = set()
    deliveries = []
    for item in available_items + assigned_items:
        if item.id in seen_ids:
            continue
        seen_ids.add(item.id)
        serialized = _serialize_delivery_item(item, current_user.id)
        if serialized:
            deliveries.append(serialized)
    return render_template(
        'rider/deliveries.html',
        username=current_user.email,
        deliveries=deliveries,
        on_shift=on_shift,
        shift_value=shift_value,
        shift_label=shift_label,
    )


@rider_bp.route('/rider/earnings')
@login_required
def earnings():
    if not _ensure_rider_access():
        return redirect(url_for('main.profile'))
    rider_profile = _get_rider_profile_obj(current_user.id)
    snapshot = _build_rider_earnings_snapshot(rider_profile, current_user.id)
    breakdown = [
        {
            'label': 'Completed Pickups',
            'count': snapshot['pickup_count'],
            'rate': PICKUP_EARNING_RATE,
            'amount': snapshot['pickup_amount'],
        },
        {
            'label': 'Delivered Orders',
            'count': snapshot['delivery_count'],
            'rate': DELIVERY_EARNING_RATE,
            'amount': snapshot['delivery_amount'],
        },
    ]
    return render_template(
        'rider/earnings_payout.html',
        username=current_user.email,
        rider=rider_profile,
        breakdown=breakdown,
        total_earned=snapshot['total_earned'],
        available_balance=snapshot['available_balance'],
        pending_payout_amount=snapshot['pending_payout_amount'],
        total_paid=snapshot['total_paid'],
        last_payout=snapshot['last_payout'],
        payout_history=snapshot['payout_history'],
        pickup_rate=PICKUP_EARNING_RATE,
        delivery_rate=DELIVERY_EARNING_RATE,
    )


@rider_bp.route('/rider/payouts/request', methods=['POST'])
@login_required
def rider_request_payout():
    if not _ensure_rider_access():
        return redirect(url_for('main.profile'))

    rider_profile = _get_rider_profile_obj(current_user.id)
    if not rider_profile:
        flash('Complete your rider profile before requesting a payout.', 'warning')
        return redirect(url_for('rider.earnings'))

    snapshot = _build_rider_earnings_snapshot(rider_profile, current_user.id)
    amount_raw = (request.form.get('amount') or '').replace(',', '').strip()
    try:
        amount = Decimal(amount_raw)
    except (InvalidOperation, TypeError):
        flash('Enter a valid payout amount.', 'danger')
        return redirect(url_for('rider.earnings'))

    amount = amount.quantize(MONEY_QUANTIZER)
    if amount <= ZERO:
        flash('Payout amount must be greater than zero.', 'danger')
        return redirect(url_for('rider.earnings'))
    if amount > snapshot['available_balance']:
        flash('Requested amount exceeds your available balance.', 'danger')
        return redirect(url_for('rider.earnings'))

    gcash_name = (request.form.get('gcash_name') or request.form.get('gcashName') or '').strip()
    gcash_number = (request.form.get('gcash_number') or request.form.get('gcashNumber') or '').strip()
    if not gcash_name:
        gcash_name = getattr(current_user, 'username', None) or current_user.email
    if not gcash_number:
        flash('Provide a GCash number so the admin can send your payout.', 'danger')
        return redirect(url_for('rider.earnings'))
    if gcash_number and not gcash_number.replace('-', '').replace(' ', '').isdigit():
        flash('GCash number should contain digits only.', 'danger')
        return redirect(url_for('rider.earnings'))

    payout_request = RiderPayoutRequest(
        rider_id=rider_profile.id,
        amount=amount,
        status='pending',
        gcash_name=gcash_name,
        gcash_number=gcash_number,
        notes=request.form.get('notes') or request.form.get('remarks'),
    )

    try:
        db.session.add(payout_request)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        current_app.logger.error('Failed to submit rider payout request: %s', exc)
        flash('Unable to submit payout request right now. Please try again.', 'danger')
        return redirect(url_for('rider.earnings'))

    flash('Payout request sent. The admin team will transfer funds to your GCash after verification.', 'success')
    return redirect(url_for('rider.earnings'))


@rider_bp.route('/rider/performance')
@login_required
def performance():
    if not _ensure_rider_access():
        return redirect(url_for('main.profile'))
    # Performance page removed per request — redirect to dashboard.
    return redirect(url_for('rider.rider_dashboard'))


@rider_bp.route('/rider/profile', methods=['GET', 'POST'])
@login_required
def profile_settings():
    if not _ensure_rider_access():
        return redirect(url_for('main.profile'))

    # Load or create the Rider profile record
    rider = Rider.query.filter_by(user_id=current_user.id).first()
    if request.method == 'POST':
        # If the user clicked the "send password reset" button
        if request.form.get('action') == 'send_reset':
            user = AuthService.get_user_by_email(current_user.email)
            if user:
                success, error = AuthService.send_password_reset_email(user)
                if success:
                    flash('A password reset email has been sent to your email address.', 'info')
                else:
                    flash(f'Error sending reset email: {error}', 'danger')
            else:
                # Don't reveal whether an account exists
                flash('A password reset email has been sent to your email address.', 'info')
            return redirect(url_for('rider.profile_settings'))

        # Otherwise treat as profile update
        # Basic editable fields (safe, minimal validation)
        name = request.form.get('name') or request.form.get('username')
        phone = request.form.get('phone')
        license_number = request.form.get('license_number')
        vehicle_type = request.form.get('vehicle_type')
        vehicle_number = request.form.get('vehicle_number')
        shift_choice = request.form.get('availability_status') or request.form.get('shift')

        # Update User name/username if provided
        if name:
            # prefer 'username' field on User model
            try:
                current_user.username = name
            except Exception:
                pass

        # Ensure rider row exists
        if not rider:
            rider = Rider(user_id=current_user.id)
            db.session.add(rider)

        # Update rider fields
        if phone is not None:
            rider.phone = phone
        if license_number is not None:
            rider.license_number = license_number
        if vehicle_type is not None:
            rider.vehicle_type = vehicle_type
        if vehicle_number is not None:
            rider.vehicle_number = vehicle_number
        normalized_shift = _normalize_shift_choice(shift_choice)
        if normalized_shift:
            rider.availability_status = normalized_shift

        # Persist changes
        try:
            db.session.commit()
            flash('Profile updated successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Could not save profile. Please try again.', 'danger')

        return redirect(url_for('rider.profile_settings'))

    # GET: render editable form
    shift_value, shift_label = _get_rider_shift_label(rider)
    return render_template(
        'rider/profile_settings.html',
        username=current_user.email,
        user=current_user,
        rider=rider,
        shift_options=RIDER_SHIFT_OPTIONS,
        shift_value=shift_value,
        shift_label=shift_label,
        on_shift=_is_rider_on_shift(rider),
    )


@rider_bp.route('/rider/map')
@login_required
def map_navigation():
    if not _ensure_rider_access():
        return redirect(url_for('main.profile'))
    # Map & Navigation removed from rider area per request.
    # Redirect to rider dashboard instead of rendering a map page.
    return redirect(url_for('rider.rider_dashboard'))


@rider_bp.route('/rider/notifications')
@login_required
def notifications():
    if not _ensure_rider_access():
        return redirect(url_for('main.profile'))
    return render_template('rider/notifications_alerts.html', username=current_user.email)


@rider_bp.route('/rider/communication')
@login_required
def communication_tools():
    if not _ensure_rider_access():
        return redirect(url_for('main.profile'))
    # Communication tools page removed — redirect riders to their dashboard.
    flash('Communication tools have been removed.', 'info')
    return redirect(url_for('rider.rider_dashboard'))
