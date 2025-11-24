from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..models import Rider, User
from .. import db
from project.services.auth_service import AuthService

rider_bp = Blueprint('rider', __name__)


def _ensure_rider_access():
    if (getattr(current_user, 'role', '') or '').lower() != 'rider' or not getattr(current_user, 'is_approved', False):
        flash("You don't have access to the rider area.", 'warning')
        return False
    return True


@rider_bp.route('/rider/dashboard')
@login_required
def rider_dashboard():
    if not _ensure_rider_access():
        return redirect(url_for('main.profile'))
    return render_template('rider/rider_dashboard.html', username=current_user.email)


@rider_bp.route('/rider/pickup-management')
@login_required
def pickup_management():
    if not _ensure_rider_access():
        return redirect(url_for('main.profile'))
    return render_template('rider/pickup_management.html', username=current_user.email)


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
