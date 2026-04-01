from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from flask_socketio import emit, join_room, leave_room
from app.models.user import User, Message
from app import db, socketio
from datetime import datetime

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/')
@login_required
def index():
    # 获取有过消息往来的用户
    from sqlalchemy import or_
    messages = Message.query.filter(
        or_(Message.sender_id == current_user.id,
            Message.receiver_id == current_user.id)
    ).order_by(Message.created_at.desc()).all()
    
    contact_ids = set()
    for m in messages:
        if m.sender_id != current_user.id:
            contact_ids.add(m.sender_id)
        if m.receiver_id != current_user.id:
            contact_ids.add(m.receiver_id)
    
    contacts = User.query.filter(User.id.in_(contact_ids)).all()
    # 好友也显示
    for f in current_user.friends:
        if f not in contacts:
            contacts.append(f)
    
    return render_template('chat/index.html', contacts=contacts)

@chat_bp.route('/with/<int:user_id>')
@login_required
def chat_with(user_id):
    other = User.query.get_or_404(user_id)
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.created_at.asc()).all()
    
    # 标记已读
    for m in messages:
        if m.receiver_id == current_user.id and not m.is_read:
            m.is_read = True
    db.session.commit()
    
    contacts = list(current_user.friends)
    return render_template('chat/chat.html', other=other, messages=messages, contacts=contacts)

@chat_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    receiver_id = request.form.get('receiver_id', type=int)
    content = request.form.get('content', '').strip()
    if not content or not receiver_id:
        return jsonify({'error': '参数错误'}), 400
    msg = Message(sender_id=current_user.id, receiver_id=receiver_id, content=content)
    db.session.add(msg)
    db.session.commit()
    return jsonify({
        'id': msg.id,
        'content': msg.content,
        'created_at': msg.created_at.strftime('%H:%M'),
        'sender_id': current_user.id
    })

# SocketIO events
@socketio.on('join')
def on_join(data):
    room = data.get('room')
    join_room(room)

@socketio.on('send_message')
def handle_message(data):
    room = data.get('room')
    content = data.get('content', '').strip()
    receiver_id = data.get('receiver_id')
    if content and receiver_id:
        msg = Message(sender_id=current_user.id, receiver_id=receiver_id, content=content)
        db.session.add(msg)
        db.session.commit()
        emit('new_message', {
            'content': content,
            'sender_id': current_user.id,
            'sender_name': current_user.nickname or current_user.username,
            'sender_avatar': current_user.avatar,
            'created_at': msg.created_at.strftime('%H:%M')
        }, room=room)
