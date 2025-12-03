from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from datetime import datetime

from ..models import Rider, User, PickupRequest, PickupRequestItem, Order
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
    pickups = _rider_pickup_queryset('available', current_user.id).limit(25).all()
    pickup_rows = [_serialize_pickup_for_rider(pickup, current_user.id) for pickup in pickups]
    return render_template(
        'rider/pickup_management.html',
        username=current_user.email,
        pickups=pickup_rows,
    )


@rider_bp.route('/rider/api/pickups')
@login_required
def pickup_list_api():
    if not _ensure_rider_access():
        return jsonify({'success': False, 'error': "You don't have access to pickups."}), 403

    scope = request.args.get('scope', 'available')
    pickups = _rider_pickup_queryset(scope, current_user.id).all()
    return jsonify({
        'success': True,
        'pickups': [_serialize_pickup_for_rider(pickup, current_user.id) for pickup in pickups],
    })


@rider_bp.route('/rider/api/pickups/<int:pickup_id>/accept', methods=['POST'])
@login_required
def pickup_accept_api(pickup_id):
    if not _ensure_rider_access():
        return jsonify({'success': False, 'error': "You don't have access to pickups."}), 403

    pickup_request = (
        PickupRequest.query.filter_by(id=pickup_id)
        .options(joinedload(PickupRequest.items))
        .first_or_404()
    )

    if pickup_request.rider_user_id and pickup_request.rider_user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Pickup already assigned to another rider.'}), 400

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
        item.status = 'picked_up'
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

    if mark_complete:
        pickup_request.mark_status('completed')
        pickup_request.completed_at = now

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Unable to update pickup.'}), 500

    return jsonify({'success': True, 'pickup': _serialize_pickup_for_rider(pickup_request, current_user.id)})


@rider_bp.route('/rider/delivery-management')
@login_required
def delivery_management():
    if not _ensure_rider_access():
        return redirect(url_for('main.profile'))
    return render_template('rider/delivery_management.html', username=current_user.email)


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
    return render_template('rider/deliveries.html', username=current_user.email)


@rider_bp.route('/rider/earnings')
@login_required
def earnings():
    if not _ensure_rider_access():
        return redirect(url_for('main.profile'))
    # Restore Earnings/Payout page for riders.
    return render_template('rider/earnings_payout.html', username=current_user.email)


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

        # Persist changes
        try:
            db.session.commit()
            flash('Profile updated successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Could not save profile. Please try again.', 'danger')

        return redirect(url_for('rider.profile_settings'))

    # GET: render editable form
    return render_template(
        'rider/profile_settings.html', username=current_user.email, user=current_user, rider=rider
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
