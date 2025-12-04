"""
Admin routes for managing user approvals and viewing admin dashboard
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from flask_mail import Message
from project import db, mail
from project.models import User, SiteSetting, Seller, Rider, Warning, RiderPayoutRequest
from project.models import ChatMessage
from project.services.auth_service import AuthService
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from decimal import Decimal

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
    # Robust fallback: explicitly find distinct user_ids from chat_messages, then load Users
    from sqlalchemy import func
    out = []
    seen_ids = set()
    try:
        # Get distinct user_ids who appear in chat_messages
        uids = [r[0] for r in db.session.query(ChatMessage.user_id).distinct().all()]
        # Load last message and unread count per user
        for uid in uids:
            if uid == current_user.id:
                continue
            user = User.query.get(uid)
            if not user:
                continue
            # find last message
            last_msg = ChatMessage.query.filter_by(user_id=user.id).order_by(ChatMessage.created_at.desc()).first()
            if not last_msg:
                continue
            # unread count (user->admin messages that are not read)
            try:
                unread = ChatMessage.query.filter_by(user_id=user.id, is_from_admin=False).filter(ChatMessage.is_read.is_(False)).count()
            except Exception:
                # fallback: count all user messages if is_read not available
                unread = ChatMessage.query.filter_by(user_id=user.id, is_from_admin=False).count()

            out.append({
                'id': user.id,
                'name': (user.username or user.email),
                'role': (user.role or '').lower(),
                'last_at': last_msg.created_at.isoformat() if last_msg.created_at else None,
                'last_body': (last_msg.body[:120] if last_msg and last_msg.body else None),
                'unread': int(unread) if unread is not None else 0,
            })
            seen_ids.add(user.id)
    except Exception:
        current_app.logger.exception('Error building contact list from chat_messages')

    # If no users found from messages, fall back to recent non-admin users (so admin can start chats)
    if not out:
        other_users = User.query.filter(User.id != current_user.id, User.role != 'admin').order_by(User.created_at.desc()).limit(200).all()
        for u in other_users:
            if u.id in seen_ids:
                continue
            seen_ids.add(u.id)
            out.append({
                'id': u.id,
                'name': (u.username or u.email),
                'role': (u.role or '').lower(),
                'last_at': None,
                'last_body': None,
                'unread': 0,
            })

    # sort by last_at desc, placing None at the end
    out.sort(key=lambda item: item['last_at'] or '', reverse=True)
    return jsonify({'contacts': out})


@admin_bp.get('/chat/debug')
@login_required
def chat_debug():
    """Temporary debug endpoint: shows chat_messages and user stats for debugging contact list."""
    try:
        total_users = User.query.count()
        non_admin_users = User.query.filter(User.role != 'admin').count()
        total_messages = ChatMessage.query.count()
        # distinct user ids appearing in chat_messages
        distinct_uids = [r[0] for r in db.session.query(ChatMessage.user_id).distinct().limit(50).all()]
        sample_msgs = []
        rows = db.session.query(ChatMessage).order_by(ChatMessage.created_at.desc()).limit(20).all()
        for m in rows:
            sample_msgs.append({'id': m.id, 'user_id': m.user_id, 'admin_id': m.admin_id, 'is_from_admin': bool(m.is_from_admin), 'created_at': (m.created_at.isoformat() if m.created_at else None), 'body': (m.body[:120] if m.body else None), 'attachment': getattr(m, 'attachment', None), 'is_read': bool(getattr(m, 'is_read', False))})
        # Build user summaries for the distinct user ids so the client can render them
        users = []
        try:
            for uid in distinct_uids:
                u = User.query.get(uid)
                if not u:
                    continue
                users.append({
                    'id': u.id,
                    'name': (u.username or u.email),
                    'email': u.email,
                    'username': u.username,
                    'role': (u.role or '').lower(),
                    'created_at': (u.created_at.isoformat() if u.created_at else None),
                })
        except Exception:
            current_app.logger.exception('Error building user summaries in chat_debug')

        return jsonify({
            'ok': True,
            'total_users': total_users,
            'non_admin_users': non_admin_users,
            'total_messages': total_messages,
            'distinct_user_ids_in_messages': distinct_uids,
            'users': users,
            'sample_messages': sample_msgs,
            'current_admin_id': current_user.id,
        })
    except Exception:
        current_app.logger.exception('Error in chat_debug')
        return jsonify({'ok': False, 'error': 'debug failed'})


@admin_bp.get('/chat/messages/<int:user_id>')
@login_required
def chat_messages(user_id):
    user = User.query.get_or_404(user_id)
    out = []
    try:
        msgs = ChatMessage.query.filter_by(user_id=user.id).order_by(ChatMessage.created_at.asc()).all()
        for m in msgs:
            out.append({
                'id': m.id,
                'body': m.body,
                'is_from_admin': bool(m.is_from_admin),
                'created_at': m.created_at.isoformat(),
                'attachment': getattr(m, 'attachment', None),
                'is_read': bool(getattr(m, 'is_read', False)),
                'sender_name': m.sender_name or (user.username or user.email),
                'sender_role': m.sender_role,
            })
        # mark user messages as read when admin opens the conversation
        try:
            (ChatMessage.query.filter_by(user_id=user.id, is_from_admin=False)
                .filter(ChatMessage.is_read.is_(False)).update({ 'is_read': True }))
            db.session.commit()
        except Exception:
            db.session.rollback()
    except Exception:
        # Fallback: DB schema might be missing columns (e.g. attachment/is_read).
        # Inspect available columns and SELECT only those to avoid errors.
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            cols = [c.get('name') for c in inspector.get_columns('chat_messages')] if 'chat_messages' in inspector.get_table_names() else []
            fields = ['id', 'body', 'is_from_admin', 'created_at', 'sender_name', 'sender_role']
            if 'attachment' in cols:
                fields.insert(4, 'attachment')
            if 'is_read' in cols and 'is_read' not in fields:
                # ensure is_read is present so we can show seen/delivered
                fields.insert( (4 if 'attachment' in cols else 4) + 1, 'is_read')
            sql = f"SELECT {', '.join(fields)} FROM chat_messages WHERE user_id = :uid ORDER BY created_at ASC"
            rows = db.session.execute(sql, {'uid': user.id}).fetchall()
            for r in rows:
                # map columns back to names
                idx = 0
                _id = r[idx]; idx += 1
                _body = r[idx]; idx += 1
                _is_from_admin = bool(r[idx]); idx += 1
                _created = r[idx]; idx += 1
                _attachment = None
                _is_read = False
                if 'attachment' in cols:
                    _attachment = r[idx]; idx += 1
                if 'is_read' in cols:
                    _is_read = bool(r[idx]); idx += 1
                _sender_name = r[idx] if idx < len(r) else None; idx += 1
                _sender_role = r[idx] if idx < len(r) else None
                out.append({
                    'id': _id,
                    'body': _body,
                    'is_from_admin': _is_from_admin,
                    'created_at': (_created.isoformat() if _created else None),
                    'attachment': _attachment,
                    'is_read': _is_read,
                    'sender_name': _sender_name or (user.username or user.email),
                    'sender_role': _sender_role,
                })
            # If we were able to read is_read column, mark user->admin messages as read
            try:
                if 'is_read' in cols:
                    from sqlalchemy import text
                    db.session.execute(text("UPDATE chat_messages SET is_read = 1 WHERE user_id = :uid AND is_from_admin = 0 AND (is_read = 0 OR is_read IS NULL)"), {'uid': user.id})
                    db.session.commit()
            except Exception:
                db.session.rollback()
        except Exception:
            current_app.logger.exception('Error fetching chat messages for admin view')

    return jsonify({'messages': out, 'user': {'id': user.id, 'name': (user.username or user.email), 'role': user.role}})


@admin_bp.post('/chat/messages/<int:user_id>/send')
@login_required
def admin_send_message(user_id):
    user = User.query.get_or_404(user_id)
    # Accept body from form or JSON, and also allow a file-only send (no body)
    body = None
    try:
        if request.form and request.form.get('body'):
            body = request.form.get('body')
        else:
            data = request.get_json(silent=True)
            if isinstance(data, dict):
                body = data.get('body')
    except Exception:
        current_app.logger.exception('Error parsing admin chat send payload')

    # normalize uploaded file (allow file-only sends)
    uploaded = request.files.get('file')
    if uploaded and getattr(uploaded, 'filename', '') == '':
        uploaded = None

    if not body and not uploaded:
        return jsonify({'error': 'Missing body or attachment'}), 400
    try:
        # Inspect DB schema and fall back to a raw INSERT if optional columns (like
        # `is_read`) are not present to avoid SQL errors on schemaversion mismatch.
        from sqlalchemy import inspect, text
        inspector = inspect(db.engine)
        table_names = inspector.get_table_names()
        cols = [c.get('name') for c in inspector.get_columns('chat_messages')] if 'chat_messages' in table_names else []
        has_is_read = 'is_read' in cols
        has_attachment_col = 'attachment' in cols

        # Handle optional file uploaded by admin (client sends as 'file')
        attachment_path = None
        attachment_skipped = False
        if uploaded:
            filename = secure_filename(uploaded.filename)
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'chat')
            os.makedirs(upload_dir, exist_ok=True)
            save_path = os.path.join(upload_dir, filename)
            if os.path.exists(save_path):
                name, ext = os.path.splitext(filename)
                filename = f"{name}-{int(datetime.now().timestamp())}{ext}"
                save_path = os.path.join(upload_dir, filename)
            uploaded.save(save_path)
            attachment_path = f"/static/uploads/chat/{filename}"
            try:
                if 'chat_messages' in table_names:
                    if 'attachment' not in cols:
                        attachment_skipped = True
                    else:
                        attachment_skipped = False
            except Exception:
                attachment_skipped = False

        # ensure body is never NULL in DB insert
        safe_body = body or ''

        if 'chat_messages' not in table_names or not has_is_read:
            insert_cols = ['user_id', 'admin_id', 'sender_name', 'sender_role', 'body', 'is_from_admin']
            params = {
                'user_id': user.id,
                'admin_id': current_user.id,
                'sender_name': (getattr(current_user, 'username', None) or getattr(current_user, 'email', None)),
                'sender_role': 'admin',
                'body': safe_body,
                'is_from_admin': True,
            }
            if has_attachment_col and not attachment_skipped and attachment_path:
                insert_cols.insert(-1, 'attachment')
                params['attachment'] = attachment_path

            sql = f"INSERT INTO chat_messages ({', '.join(insert_cols)}) VALUES ({', '.join(':' + c for c in insert_cols)})"
            db.session.execute(text(sql), params)
            db.session.commit()
            try:
                row = db.session.execute(text("SELECT id, created_at, sender_name, body, attachment, is_from_admin, is_read FROM chat_messages WHERE user_id = :uid AND admin_id = :aid ORDER BY id DESC LIMIT 1"), {'uid': user.id, 'aid': current_user.id}).fetchone()
                msg_id = row[0] if row else None
                created_at = row[1] if row and row[1] else None
                sender_name = row[2] if row else (getattr(current_user, 'username', None) or getattr(current_user, 'email', None))
                body_text = row[3] if row and len(row) > 3 else None
                attachment_val = row[4] if row and len(row) > 4 else None
                is_from_admin_val = bool(row[5]) if row and len(row) > 5 else True
                is_read_val = bool(row[6]) if row and len(row) > 6 else False
            except Exception:
                msg_id = None
                created_at = None
                sender_name = (getattr(current_user, 'username', None) or getattr(current_user, 'email', None))
            class _R: pass
            msg = _R()
            msg.id = msg_id
            msg.created_at = created_at
            msg.sender_name = sender_name
            # attach optional attributes to msg for convenience
            try:
                msg.body = body_text
                msg.attachment = attachment_val
                msg.is_from_admin = is_from_admin_val
                msg.is_read = is_read_val
            except Exception:
                pass
        else:
            common = dict(
                user_id=user.id,
                admin_id=current_user.id,
                sender_name=(getattr(current_user, 'username', None) or getattr(current_user, 'email', None)),
                sender_role='admin',
                body=safe_body,
                is_from_admin=True,
            )
            if not attachment_skipped and has_attachment_col and attachment_path:
                common['attachment'] = attachment_path
            msg = ChatMessage(**common)
            db.session.add(msg)
            db.session.commit()
            # after ORM insert, ensure we return the persisted values
            try:
                refreshed = ChatMessage.query.get(msg.id)
                if refreshed:
                    msg.body = refreshed.body
                    msg.attachment = getattr(refreshed, 'attachment', None)
                    msg.is_from_admin = bool(refreshed.is_from_admin)
                    msg.is_read = bool(getattr(refreshed, 'is_read', False))
                    msg.created_at = refreshed.created_at
            except Exception:
                pass
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


@admin_bp.route('/rider-payouts')
@login_required
def rider_payouts():
    payouts = (
        RiderPayoutRequest.query
        .order_by(RiderPayoutRequest.requested_at.desc())
        .limit(200)
        .all()
    )
    pending = [p for p in payouts if p.status == 'pending']
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)
    processed_this_month = [
        p for p in payouts
        if p.status == 'paid' and p.processed_at and p.processed_at >= month_start
    ]
    stats = {
        'pending_count': len(pending),
        'pending_total': sum(((p.amount or Decimal('0')) for p in pending), Decimal('0')),
        'processed_this_month': len(processed_this_month),
        'processed_total': sum(((p.amount or Decimal('0')) for p in processed_this_month), Decimal('0')),
    }
    return render_template('admin/rider_payouts.html', payouts=payouts, stats=stats)


@admin_bp.post('/rider-payouts/<int:payout_id>/status')
@login_required
def rider_payout_update(payout_id):
    payout = RiderPayoutRequest.query.get_or_404(payout_id)
    new_status = (request.form.get('status') or '').strip().lower()
    valid_statuses = {'pending', 'paid', 'rejected'}
    if new_status not in valid_statuses:
        flash('Invalid payout status submitted.', 'danger')
        return redirect(url_for('admin.rider_payouts'))

    payout.status = new_status
    payout.admin_notes = request.form.get('admin_notes') or payout.admin_notes
    reference_code = request.form.get('reference_code') or request.form.get('reference')
    if reference_code:
        payout.reference_code = reference_code

    if new_status in {'paid', 'rejected'}:
        payout.processed_at = datetime.utcnow()
        payout.processed_by_id = current_user.id
    else:
        payout.processed_at = None
        payout.processed_by_id = None

    try:
        db.session.commit()
        flash('Payout status updated.', 'success')
    except Exception as exc:
        db.session.rollback()
        current_app.logger.error('Failed to update rider payout %s: %s', payout_id, exc)
        flash('Unable to update payout right now.', 'danger')

    return redirect(url_for('admin.rider_payouts'))


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
