from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from project import db
from project.models import ChatMessage, User
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timezone, timedelta

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')


@chat_bp.post('/send')
@login_required
def send_message():
    """Endpoint for logged-in users (buyer/seller/rider) to send message to admin."""
    # Robustly parse body from form data or JSON payload
    body = None
    try:
        if request.form and request.form.get('body'):
            body = request.form.get('body')
        else:
            data = request.get_json(silent=True)
            if isinstance(data, dict):
                body = data.get('body')
    except Exception:
        current_app.logger.exception('Error parsing chat send payload')

    # Allow sending when either a body or a file is provided
    uploaded = request.files.get('file')
    # normalize empty file inputs
    if uploaded and getattr(uploaded, 'filename', '') == '':
        uploaded = None

    if not body and not uploaded:
        current_app.logger.info('Chat send called without body OR file by user_id=%s', getattr(current_user, 'id', None))
        return jsonify({'error': 'Missing body or attachment'}), 400

    try:
        # Ensure we never attempt to insert NULL into a non-nullable body column.
        safe_body = body or ''
        current_app.logger.debug('Saving chat message from user_id=%s body_len=%s file=%s', getattr(current_user, 'id', None), len(safe_body) if safe_body else 0, bool(uploaded))
        # Handle optional file upload (uploaded variable was normalized above)
        attachment_path = None
        attachment_skipped = False
        if uploaded:
            filename = secure_filename(uploaded.filename)
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'chat')
            os.makedirs(upload_dir, exist_ok=True)
            save_path = os.path.join(upload_dir, filename)
            # If same filename exists, append timestamp to avoid overwrite
            if os.path.exists(save_path):
                name, ext = os.path.splitext(filename)
                filename = f"{name}-{int(datetime.now().timestamp())}{ext}"
                save_path = os.path.join(upload_dir, filename)
            uploaded.save(save_path)
            # Save path relative to static for serving
            attachment_path = f"/static/uploads/chat/{filename}"

            # Defensive: if the DB schema doesn't have the attachment column yet
            # (migration not applied), avoid including attachment in the INSERT to
            # prevent SQL errors. We'll detect available columns via SQLAlchemy
            # inspector and drop attachment if it's not present.
            try:
                from sqlalchemy import inspect

                inspector = inspect(db.engine)
                cols = [c.get('name') for c in inspector.get_columns('chat_messages')]
                if 'attachment' not in cols:
                    current_app.logger.warning('DB missing chat_messages.attachment column; skipping attachment save in DB')
                    # keep the file on disk but mark that DB doesn't have attachment column
                    attachment_skipped = True
                    # keep attachment_path as-is on disk, but we will avoid including it in the ORM insert
                else:
                    attachment_skipped = False
            except Exception:
                # If inspection fails for any reason, proceed normally and let DB raise if needed
                attachment_skipped = False

        # Inspect DB columns so we can gracefully handle schema drift (missing optional cols)
        from sqlalchemy import inspect, text

        inspector = inspect(db.engine)
        table_names = inspector.get_table_names()
        cols = [c.get('name') for c in inspector.get_columns('chat_messages')] if 'chat_messages' in table_names else []
        has_is_read = 'is_read' in cols
        has_attachment_col = 'attachment' in cols

        # If DB is missing the `is_read` column (or other mapped columns), use a
        # safe raw INSERT that only targets existing columns to avoid SQL errors.
        if 'chat_messages' not in table_names or not has_is_read:
            insert_cols = ['user_id', 'admin_id', 'sender_name', 'sender_role', 'body', 'is_from_admin']
            params = {
                'user_id': current_user.id,
                'admin_id': None,
                'sender_name': (getattr(current_user, 'username', None) or getattr(current_user, 'email', None)),
                'sender_role': (getattr(current_user, 'role', '') or '').lower(),
                'body': safe_body,
                'is_from_admin': False,
            }
            if has_attachment_col and not attachment_skipped:
                insert_cols.insert(-1, 'attachment')
                params['attachment'] = attachment_path

            sql = f"INSERT INTO chat_messages ({', '.join(insert_cols)}) VALUES ({', '.join(':' + c for c in insert_cols)})"
            db.session.execute(text(sql), params)
            db.session.commit()

            # Fetch the last inserted message for this user so we can return id/created_at
            try:
                row = db.session.execute(text("SELECT id, created_at, sender_name FROM chat_messages WHERE user_id = :uid ORDER BY id DESC LIMIT 1"), {'uid': current_user.id}).fetchone()
                msg_id = row[0] if row else None
                created_at = row[1] if row and row[1] else None
                sender_name = row[2] if row else (getattr(current_user, 'username', None) or getattr(current_user, 'email', None))
            except Exception:
                msg_id = None
                created_at = None
                sender_name = (getattr(current_user, 'username', None) or getattr(current_user, 'email', None))
            # Build a lightweight response object similar to ORM-created one
            class _R: pass
            msg = _R()
            msg.id = msg_id
            msg.created_at = created_at
            msg.sender_name = sender_name
        else:
            # Construct ChatMessage normally when DB schema matches model
            common = dict(
                user_id=current_user.id,
                sender_name=(getattr(current_user, 'username', None) or getattr(current_user, 'email', None)),
                sender_role=(getattr(current_user, 'role', '') or '').lower(),
                body=safe_body,
                is_from_admin=False,
            )
            if not attachment_skipped and has_attachment_col:
                common['attachment'] = attachment_path
            msg = ChatMessage(**common)
            db.session.add(msg)
            db.session.commit()
    except Exception as exc:
        db.session.rollback()
        current_app.logger.exception('Error saving chat message from user_id=%s', getattr(current_user, 'id', None))
        # Return exception message in development for easier debugging
        try:
            msg = str(exc)
        except Exception:
            msg = 'internal server error'
        return jsonify({'ok': False, 'error': msg}), 500

    return jsonify({'ok': True, 'id': msg.id, 'created_at': msg.created_at.isoformat(), 'sender_name': msg.sender_name}), 201


@chat_bp.get('/my')
@login_required
def my_messages():
    """Return current user's conversation messages."""
    out = []
    try:
        msgs = ChatMessage.query.filter_by(user_id=current_user.id).order_by(ChatMessage.created_at.asc()).all()
        for m in msgs:
            out.append({
                'id': m.id,
                'body': m.body,
                'is_from_admin': bool(m.is_from_admin),
                'created_at': m.created_at.isoformat(),
                'attachment': getattr(m, 'attachment', None),
                'is_read': bool(getattr(m, 'is_read', False)),
                'sender_name': m.sender_name,
                'sender_role': m.sender_role,
            })
    except Exception:
        # Fallback when DB schema doesn't include optional columns: inspect available columns
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            cols = [c.get('name') for c in inspector.get_columns('chat_messages')] if 'chat_messages' in inspector.get_table_names() else []
            fields = ['id', 'body', 'is_from_admin', 'created_at', 'sender_name', 'sender_role']
            if 'attachment' in cols:
                fields.insert(4, 'attachment')
            if 'is_read' in cols and 'is_read' not in fields:
                fields.insert( (4 if 'attachment' in cols else 4) + 1, 'is_read')
            sql = f"SELECT {', '.join(fields)} FROM chat_messages WHERE user_id = :uid ORDER BY created_at ASC"
            rows = db.session.execute(sql, {'uid': current_user.id}).fetchall()
            for r in rows:
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
                    'sender_name': _sender_name,
                    'sender_role': _sender_role,
                })
        except Exception:
            current_app.logger.exception('Error fetching user chat messages')
    # Determine whether admin is "active" based on most recent admin message timestamp (within last 5 minutes)
    admin_online = False
    try:
        last_admin_msg = ChatMessage.query.filter_by(user_id=current_user.id, is_from_admin=True).order_by(ChatMessage.created_at.desc()).first()
        if last_admin_msg and last_admin_msg.created_at:
            created = last_admin_msg.created_at
            # make created aware in UTC if naive
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            delta = now - created
            if delta.total_seconds() <= 300:
                admin_online = True
    except Exception:
        current_app.logger.exception('Error computing admin_online')

    return jsonify({'messages': out, 'admin_online': admin_online})
