"""
Admin routes for managing user approvals and viewing admin dashboard
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from flask_mail import Message
from project import db, mail
from project.models import User, SiteSetting, Seller, Rider
from project.services.auth_service import AuthService

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.before_request
def restrict_to_admin():
    # Allow admin login routes without admin session
    if request.endpoint and request.endpoint.endswith('admin.login'):
        return
    if request.endpoint and request.endpoint.endswith('admin.login_post'):
        return
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    if (getattr(current_user, 'role', '') or '').lower() != 'admin':
        flash("Administrator access required.", 'danger')
        return redirect(url_for('main.index'))
    if getattr(current_user, 'is_suspended', False):
        flash("Administrator account is suspended.", 'danger')
        logout_user()
        return redirect(url_for('admin.login'))


@admin_bp.get('/login')
def login():
    return render_template('admin/login.html')


@admin_bp.post('/login')
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')

    user, error = AuthService.authenticate_user(email, password)
    if error:
        return "Invalid admin credentials.", 401

    if (getattr(user, 'role', '') or '').lower() != 'admin':
        return "Only admin accounts can sign in here.", 403

    login_user(user, remember=True)
    return redirect(url_for('admin.overview'))


@admin_bp.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('admin.login'))


@admin_bp.route('/profile')
@login_required
def profile():
    """Admin profile page"""
    return render_template('admin/profile.html', user=current_user)


@admin_bp.get('/')
@admin_bp.get('/overview')
@login_required
def overview():
    """Overview dashboard with statistics"""
    # KPIs
    total_users = User.query.count()
    total_buyers = User.query.filter_by(role='buyer').count()
    total_sellers = User.query.filter_by(role='seller').count()
    total_riders = User.query.filter_by(role='rider').count()
    total_pending = User.query.filter(
        User.role_requested.isnot(None),
        User.is_approved.is_(False)
    ).count()

    return render_template(
        'admin/overview.html',
        total_users=total_users,
        total_buyers=total_buyers,
        total_sellers=total_sellers,
        total_riders=total_riders,
        total_pending=total_pending
    )


@admin_bp.get('/pending')
@login_required
def pending():
    """Pending approvals page"""
    pending_requests = User.query.filter(
        User.role_requested.isnot(None),
        User.is_approved.is_(False)
    ).order_by(User.created_at.desc()).all()

    return render_template('admin/pending.html', pending_requests=pending_requests)


@admin_bp.get('/users')
@login_required
def users():
    """User management page"""
    buyers = User.query.filter_by(role='buyer', is_approved=True).order_by(User.created_at.desc()).all()
    sellers = User.query.filter_by(role='seller', is_approved=True).order_by(User.created_at.desc()).all()
    riders = User.query.filter_by(role='rider', is_approved=True).order_by(User.created_at.desc()).all()
    pending_requests = User.query.filter(
        User.role_requested.isnot(None),
        User.is_approved.is_(False)
    ).order_by(User.created_at.desc()).all()

    return render_template(
        'admin/users.html',
        buyers=buyers,
        sellers=sellers,
        riders=riders,
        pending_requests=pending_requests
    )


@admin_bp.get('/get-seller-details/<int:user_id>')
@login_required
def get_seller_details(user_id):
    """Get seller/rider details for the modal"""
    user = User.query.get_or_404(user_id)
    
    if not user.role_requested:
        return jsonify({'error': 'No role request found for this user'}), 404
    
    response_data = {
        'email': user.email,
        'role_requested': user.role_requested,
        'created_at': user.created_at.strftime('%B %d, %Y at %I:%M %p') if user.created_at else None,
    }
    
    # Add seller profile data if exists
    if user.role_requested == 'seller':
        seller = Seller.query.filter_by(user_id=user.id).first()
        if seller:
            response_data['seller_profile'] = {
                'business_name': seller.business_name,
                'business_type': seller.business_type,
                'business_address': seller.business_address,
                'business_city': seller.business_city,
                'business_zip': seller.business_zip,
                'business_country': seller.business_country,
                'bank_type': seller.bank_type,
                'bank_name': seller.bank_name,
                'bank_account': seller.bank_account,
                'bank_holder_name': seller.bank_holder_name,
                'tax_id': seller.tax_id,
                'store_description': seller.store_description,
            }
        else:
            response_data['seller_profile'] = None
    
    # Add rider profile data if exists
    elif user.role_requested == 'rider':
        rider = Rider.query.filter_by(user_id=user.id).first()
        if rider:
            response_data['rider_profile'] = {
                'phone': rider.phone,
                'license_number': rider.license_number,
                'vehicle_type': rider.vehicle_type,
                'vehicle_number': rider.vehicle_number,
            }
        else:
            response_data['rider_profile'] = None
    
    return jsonify(response_data)


@admin_bp.post('/approve-request/<int:user_id>')
@login_required
def approve_request(user_id):
    """Approve a user's role request"""
    user = User.query.get_or_404(user_id)
    if not user.role_requested or user.is_approved:
        flash('No pending request for this user.', 'warning')
        return redirect(url_for('admin.users'))

    try:
        new_role = user.role_requested
        user.role = new_role
        user.is_approved = True
        user.role_requested = None
        db.session.commit()

        _send_notification(
            user,
            subject=f"Your {new_role} request has been approved",
            body=(
                f"Hi {user.email},\n\n"
                f"Good news! Your request to become a {new_role} has been approved. "
                "You may now log in and use the new dashboard.\n\n"
                "Thanks,\nDione Admin Team"
            )
        )
        flash(f"{user.email}'s request approved as {new_role}.", 'success')
    except Exception as exc:
        db.session.rollback()
        flash(f"Error approving request: {exc}", 'danger')

    return redirect(url_for('admin.users'))


@admin_bp.post('/reject-request/<int:user_id>')
@login_required
def reject_request(user_id):
    """Reject a user's role request"""
    user = User.query.get_or_404(user_id)
    if not user.role_requested:
        flash('No pending request for this user.', 'warning')
        return redirect(url_for('admin.users'))

    try:
        rejected_role = user.role_requested
        user.role_requested = None
        user.is_approved = False
        db.session.commit()

        _send_notification(
            user,
            subject=f"Your {rejected_role} request was declined",
            body=(
                f"Hi {user.email},\n\n"
                f"We reviewed your request to become a {rejected_role} but had to decline it at this time. "
                "Feel free to update your profile and try again.\n\n"
                "Thanks,\nDione Admin Team"
            )
        )
        flash(f"{user.email}'s request declined.", 'info')
    except Exception as exc:
        db.session.rollback()
        flash(f"Error declining request: {exc}", 'danger')

    return redirect(url_for('admin.users'))



@admin_bp.get('/orders')
@login_required
def orders():
    """Order history page"""
    # Placeholder for orders - will be implemented when Order model exists
    return render_template('admin/orders.html')


@admin_bp.get('/sales')
@login_required
def sales():
    """Sales reports page"""
    # Placeholder for sales reports - will be implemented when Order model exists
    return render_template('admin/sales.html')


@admin_bp.get('/products')
@login_required
def products():
    """Product management placeholder"""
    return render_template('admin/admin_products_management.html')


@admin_bp.get('/sellers')
@login_required
def sellers():
    """Seller management placeholder"""
    return render_template('admin/admin_sellers_management.html')


@admin_bp.get('/riders')
@login_required
def riders():
    """Rider management placeholder"""
    return render_template('admin/admin_riders_management.html')


@admin_bp.get('/commission')
@login_required
def commission():
    """Commission & payouts placeholder"""
    return render_template('admin/admin_commission_management.html')


@admin_bp.get('/website')
@login_required
def website_settings_page():
    """Website settings placeholder"""
    return render_template('admin/website.html')


@admin_bp.get('/support')
@login_required
def support_center():
    """Support center placeholder"""
    return render_template('admin/support.html')


@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Settings page"""
    defaults = {
        'support_email': 'support@example.com',
        'support_phone': '+63 900 000 0000',
        'auto_approve_sellers': 'false',
        'auto_approve_riders': 'false',
        'maintenance_mode': 'false'
    }
    settings_map = _ensure_settings(defaults)
    if request.method == 'POST':
        updates = {
            'support_email': request.form.get('support_email', '').strip(),
            'support_phone': request.form.get('support_phone', '').strip(),
            'auto_approve_sellers': 'true' if request.form.get('auto_approve_sellers') else 'false',
            'auto_approve_riders': 'true' if request.form.get('auto_approve_riders') else 'false',
            'maintenance_mode': 'true' if request.form.get('maintenance_mode') else 'false'
        }
        _save_settings(updates)
        flash('Settings updated.', 'success')
        return redirect(url_for('admin.settings'))

    bools = {
        'auto_approve_sellers': _to_bool(settings_map['auto_approve_sellers']),
        'auto_approve_riders': _to_bool(settings_map['auto_approve_riders']),
        'maintenance_mode': _to_bool(settings_map['maintenance_mode'])
    }
    return render_template('admin/settings.html', settings=settings_map, flags=bools)


def _ensure_settings(defaults):
    """Ensure settings exist in DB and return dict of values."""
    settings_map = {}
    created = False
    for key, default in defaults.items():
        setting = SiteSetting.query.filter_by(key=key).first()
        if not setting:
            setting = SiteSetting(key=key, value=str(default))
            db.session.add(setting)
            created = True
        settings_map[key] = setting.value
    if created:
        db.session.commit()
    return settings_map


def _save_settings(updates: dict):
    changed = False
    for key, value in updates.items():
        setting = SiteSetting.query.filter_by(key=key).first()
        if setting:
            if setting.value != value:
                setting.value = value
                changed = True
        else:
            db.session.add(SiteSetting(key=key, value=value))
            changed = True
    if changed:
        db.session.commit()


def _to_bool(value):
    return str(value).lower() in ('1', 'true', 'yes', 'on')


def _send_notification(user: User, subject: str, body: str):
    if not user.email:
        return
    sender = current_app.config.get('MAIL_USERNAME') or current_app.config.get('MAIL_DEFAULT_SENDER')
    msg = Message(
        subject=subject,
        recipients=[user.email],
        body=body,
        sender=sender
    )
    mail.send(msg)


@admin_bp.post('/users/<int:user_id>/suspend')
@login_required
def user_suspend(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot suspend your own admin account.", 'warning')
        return redirect(url_for('admin.users'))
    try:
        user.is_suspended = True
        db.session.commit()
        flash(f"{user.email} has been suspended.", 'info')
    except Exception as exc:
        db.session.rollback()
        flash(f"Error suspending user: {exc}", 'danger')
    return redirect(url_for('admin.users'))


@admin_bp.post('/users/<int:user_id>/reactivate')
@login_required
def user_reactivate(user_id):
    user = User.query.get_or_404(user_id)
    try:
        user.is_suspended = False
        db.session.commit()
        flash(f"{user.email} has been reactivated.", 'success')
    except Exception as exc:
        db.session.rollback()
        flash(f"Error reactivating user: {exc}", 'danger')
    return redirect(url_for('admin.users'))


@admin_bp.post('/users/<int:user_id>/delete')
@login_required
def user_delete(user_id):
    """Delete a user and all associated data (OAuth records deleted first)"""
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot delete your own admin account.", 'warning')
        return redirect(url_for('admin.users'))
    try:
        user_email = user.email
        # Delete OAuth records first to avoid foreign key constraint issues
        for oauth in user.oauth:
            db.session.delete(oauth)
        db.session.flush()  # Ensure OAuth records are deleted before user
        db.session.delete(user)
        db.session.commit()
        flash(f"User '{user_email}' and all associated data have been permanently deleted.", 'success')
    except Exception as exc:
        db.session.rollback()
        flash(f"Error deleting user: {str(exc)}", 'danger')
    return redirect(url_for('admin.users'))
