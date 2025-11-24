from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from project import db
from project.models import ChatMessage, User

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

    if not body:
        current_app.logger.info('Chat send called without body by user_id=%s', getattr(current_user, 'id', None))
        return jsonify({'error': 'Missing body'}), 400

    try:
        current_app.logger.debug('Saving chat message from user_id=%s body_len=%s', getattr(current_user, 'id', None), len(body) if body else 0)
        msg = ChatMessage(
            user_id=current_user.id,
            sender_name=(getattr(current_user, 'username', None) or getattr(current_user, 'email', None)),
            sender_role=(getattr(current_user, 'role', '') or '').lower(),
            body=body,
            is_from_admin=False,
        )
        db.session.add(msg)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        current_app.logger.exception('Error saving chat message from user_id=%s', getattr(current_user, 'id', None))
        return jsonify({'ok': False, 'error': 'internal server error'}), 500

    return jsonify({'ok': True, 'id': msg.id, 'created_at': msg.created_at.isoformat(), 'sender_name': msg.sender_name}), 201


@chat_bp.get('/my')
@login_required
def my_messages():
    """Return current user's conversation messages."""
    msgs = ChatMessage.query.filter_by(user_id=current_user.id).order_by(ChatMessage.created_at.asc()).all()
    out = []
    for m in msgs:
        out.append({
            'id': m.id,
            'body': m.body,
            'is_from_admin': bool(m.is_from_admin),
            'created_at': m.created_at.isoformat(),
            'sender_name': m.sender_name,
            'sender_role': m.sender_role,
        })
    return jsonify({'messages': out})
