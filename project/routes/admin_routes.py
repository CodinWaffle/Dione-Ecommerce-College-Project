"""
Admin routes for managing user approvals and viewing admin dashboard
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from flask_mail import Message
from project import db, mail
from project.models import User, SiteSetting, Seller, Rider, Warning
from project.models import ChatMessage
from project.services.auth_service import AuthService

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

from jinja2 import Undefined


def _clean_for_json(obj):
    """Recursively replace Jinja2 Undefined values with None so json serialization succeeds."""
    # Primitive / simple cases
    if obj is None:
        return None
    if isinstance(obj, Undefined):
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    # Dicts
    if isinstance(obj, dict):
        return {k: _clean_for_json(v) for k, v in obj.items()}
    # Lists / tuples / sets
    if isinstance(obj, (list, tuple, set)):
        return [_clean_for_json(v) for v in obj]
    # SQLAlchemy models or other objects: try to convert common types, otherwise return as-is
    try:
        # datetime and other json-serializable types will be handled by jsonify/encoder
        return obj
    except Exception:
        return None


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
    buyers_q = User.query.filter_by(role='buyer', is_approved=True)
    sellers_q = User.query.filter_by(role='seller', is_approved=True)
    riders_q = User.query.filter_by(role='rider', is_approved=True)

    buyers = buyers_q.order_by(User.created_at.desc()).all()
    sellers = sellers_q.order_by(User.created_at.desc()).all()
    riders = riders_q.order_by(User.created_at.desc()).all()

    pending_requests = User.query.filter(
        User.role_requested.isnot(None),
        User.is_approved.is_(False)
    ).order_by(User.created_at.desc()).all()

    # Counts for dashboard stats
    buyers_count = buyers_q.count()
    sellers_count = sellers_q.count()
    riders_count = riders_q.count()
    pending_count = User.query.filter(
        User.role_requested.isnot(None),
        User.is_approved.is_(False)
    ).count()

    return render_template(
        'admin/users.html',
        buyers=buyers,
        sellers=sellers,
        riders=riders,
        pending_requests=pending_requests,
        buyers_count=buyers_count,
        sellers_count=sellers_count,
        riders_count=riders_count,
        pending_count=pending_count
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
    
    # Sanitize potential Jinja2 Undefined values before JSON serialization
    safe = _clean_for_json(response_data)
    return jsonify(safe)


@admin_bp.get('/get-warning-data/<int:user_id>')
@login_required
def get_warning_data(user_id):
    """Return warning templates and count for a user."""
    user = User.query.get_or_404(user_id)

    # Define a small set of ready-made templates (key, label, subject, body)
    templates = [
        {
            'key': 'first_warning',
            'label': 'First Warning - Minor Violation',
            'subject': 'Notice: Policy Violation - First Warning',
            'body': 'We noticed a policy violation on your account. This is a first warning. Please review our policy and correct the issue.'
        },
        {
            'key': 'second_warning',
            'label': 'Second Warning - Repeat Violation',
            'subject': 'Second Notice: Repeat Policy Violation',
            'body': 'This is your second warning for repeated policy violations. Continued issues may result in suspension.'
        },
        {
            'key': 'final_warning',
            'label': 'Final Warning - Serious Violation',
            'subject': 'Final Warning: Immediate Action Required',
            'body': 'This is a final warning for serious violations. Failure to comply will result in further disciplinary action.'
        }
    ]

    count = Warning.query.filter_by(user_id=user.id).count()

    return jsonify({
        'templates': templates,
        'warning_count': count,
        'email': user.email
    })


@admin_bp.post('/send-warning/<int:user_id>')
@login_required
def send_warning(user_id):
    """Send a warning email to a user and record it in the DB."""
    user = User.query.get_or_404(user_id)
    # Accept form data (either template_key or custom subject/body)
    template_key = request.form.get('template_key')
    subject = request.form.get('subject')
    body = request.form.get('body')

    # If template_key provided but no subject/body, map to templates above
    templates_map = {
        'first_warning': ('Notice: Policy Violation - First Warning', 'We noticed a policy violation on your account. This is a first warning. Please review our policy and correct the issue.'),
        'second_warning': ('Second Notice: Repeat Policy Violation', 'This is your second warning for repeated policy violations. Continued issues may result in suspension.'),
        'final_warning': ('Final Warning: Immediate Action Required', 'This is a final warning for serious violations. Failure to comply will result in further disciplinary action.'),
    }

    if template_key and (not subject or not body):
        tpl = templates_map.get(template_key)
        if tpl:
            subject, body = tpl

    if not subject or not body:
        flash('Missing subject or body for warning email.', 'warning')
        return redirect(url_for('admin.users'))

    try:
        # send email
        _send_notification(user, subject=subject, body=body)

        # record in DB
        w = Warning(user_id=user.id, admin_id=current_user.id, template_key=template_key, subject=subject, body=body)
        db.session.add(w)
        db.session.commit()
        flash(f'Warning sent to {user.email}.', 'success')
    except Exception as exc:
        db.session.rollback()
        flash(f'Error sending warning: {exc}', 'danger')

    return redirect(url_for('admin.users'))


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

# Legacy endpoint name used in templates: `admin.support` -> map to same view
admin_bp.add_url_rule('/support', endpoint='support', view_func=support_center, methods=['GET'])


@admin_bp.get('/chat-support')
@login_required
def chat_support():
    """Chat support dashboard"""
    return render_template('admin/chat_support.html')


@admin_bp.get('/chat/contacts')
@login_required
def chat_contacts():
    """Return list of users who have chatted (most recent first)"""
    # get users who have messages
    from sqlalchemy import func
    sub = db.session.query(
        ChatMessage.user_id,
        func.max(ChatMessage.created_at).label('last_at'),
        func.count(func.nullif(ChatMessage.is_from_admin, True)).label('unread')
    ).group_by(ChatMessage.user_id).subquery()

    # Users who have messages (ordered by last message desc)
    rows = db.session.query(User, sub.c.last_at, sub.c.unread).join(sub, User.id == sub.c.user_id).order_by(sub.c.last_at.desc()).all()

    out = []
    seen_ids = set()
    for user, last_at, unread in rows:
        if user.id == current_user.id:
            continue
        if (getattr(user, 'role', '') or '').lower() == 'admin':
            continue
        seen_ids.add(user.id)
        out.append({
            'id': user.id,
            'name': (user.username or user.email),
            'role': (user.role or '').lower(),
            'last_at': last_at.isoformat() if last_at else None,
            'unread': int(unread) if unread is not None else 0,
        })

    # Include recent users (new users) who haven't chatted yet so admin can start a conversation
    recent_users = User.query.filter(User.id != current_user.id).filter((getattr(User, 'role') != 'admin')).order_by(User.created_at.desc()).limit(50).all()
    for u in recent_users:
        if u.id in seen_ids:
            continue
        seen_ids.add(u.id)
        out.append({
            'id': u.id,
            'name': (u.username or u.email),
            'role': (u.role or '').lower(),
            'last_at': None,
            'unread': 0,
        })

    # Ensure list is ordered by most recent activity first (users with last_at first, then recent users)
    def sort_key(item):
        # Items with last_at should come before None; use ISO string -> parse not necessary, compare None
        return (0 if item['last_at'] else 1, item['last_at'] or '')

    out.sort(key=sort_key)
    return jsonify({'contacts': out})


@admin_bp.get('/chat/messages/<int:user_id>')
@login_required
def chat_messages(user_id):
    user = User.query.get_or_404(user_id)
    msgs = ChatMessage.query.filter_by(user_id=user.id).order_by(ChatMessage.created_at.asc()).all()
    out = []
    for m in msgs:
        out.append({
            'id': m.id,
            'body': m.body,
            'is_from_admin': bool(m.is_from_admin),
            'created_at': m.created_at.isoformat(),
            'sender_name': m.sender_name or (user.username or user.email),
            'sender_role': m.sender_role,
        })
    return jsonify({'messages': out, 'user': {'id': user.id, 'name': (user.username or user.email), 'role': user.role}})


@admin_bp.post('/chat/messages/<int:user_id>/send')
@login_required
def admin_send_message(user_id):
    user = User.query.get_or_404(user_id)
    body = request.form.get('body') or (request.json.get('body') if request.json else None)
    if not body:
        return jsonify({'error': 'Missing body'}), 400
    try:
        msg = ChatMessage(
            user_id=user.id,
            admin_id=current_user.id,
            sender_name=(getattr(current_user, 'username', None) or getattr(current_user, 'email', None)),
            sender_role='admin',
            body=body,
            is_from_admin=True,
        )
        db.session.add(msg)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        current_app.logger.exception('Error saving admin chat message')
        return jsonify({'ok': False, 'error': str(exc)}), 500

    return jsonify({'ok': True, 'id': msg.id, 'created_at': msg.created_at.isoformat(), 'sender_name': msg.sender_name}), 201


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
