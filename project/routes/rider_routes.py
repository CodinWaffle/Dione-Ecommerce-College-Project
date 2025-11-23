from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

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
    return render_template('rider/earnings_payout.html', username=current_user.email)


@rider_bp.route('/rider/performance')
@login_required
def performance():
    if not _ensure_rider_access():
        return redirect(url_for('main.profile'))
    return render_template('rider/performance_tracking.html', username=current_user.email)


@rider_bp.route('/rider/profile')
@login_required
def profile_settings():
    if not _ensure_rider_access():
        return redirect(url_for('main.profile'))
    return render_template('rider/profile_settings.html', username=current_user.email)


@rider_bp.route('/rider/map')
@login_required
def map_navigation():
    if not _ensure_rider_access():
        return redirect(url_for('main.profile'))
    return render_template('rider/map_navigation.html', username=current_user.email)


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
    return render_template('rider/communication_tools.html', username=current_user.email)
