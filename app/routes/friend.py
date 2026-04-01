from flask import Blueprint, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.user import User, FriendRequest
from app import db

friend_bp = Blueprint('friend', __name__)

@friend_bp.route('/send/<int:user_id>', methods=['POST'])
@login_required
def send_request(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('不能添加自己为好友。', 'warning')
        return redirect(url_for('user.profile', user_id=user_id))
    if current_user.is_friend(user):
        flash('已经是好友了。', 'info')
        return redirect(url_for('user.profile', user_id=user_id))
    existing = FriendRequest.query.filter_by(
        sender_id=current_user.id, receiver_id=user_id, status='pending').first()
    if existing:
        flash('已发送过请求，等待对方确认。', 'info')
        return redirect(url_for('user.profile', user_id=user_id))
    message = request.form.get('message', '')
    fr = FriendRequest(sender_id=current_user.id, receiver_id=user_id, message=message)
    db.session.add(fr)
    db.session.commit()
    flash('好友请求已发送！', 'success')
    return redirect(url_for('user.profile', user_id=user_id))

@friend_bp.route('/accept/<int:request_id>', methods=['POST'])
@login_required
def accept_request(request_id):
    fr = FriendRequest.query.get_or_404(request_id)
    if fr.receiver_id != current_user.id:
        flash('无权操作。', 'danger')
        return redirect(url_for('user.friend_requests'))
    fr.status = 'accepted'
    sender = User.query.get(fr.sender_id)
    if sender not in current_user.friends:
        current_user.friends.append(sender)
    if current_user not in sender.friends:
        sender.friends.append(current_user)
    db.session.commit()
    flash(f'已接受 {sender.nickname or sender.username} 的好友请求！', 'success')
    return redirect(url_for('user.friend_requests'))

@friend_bp.route('/reject/<int:request_id>', methods=['POST'])
@login_required
def reject_request(request_id):
    fr = FriendRequest.query.get_or_404(request_id)
    if fr.receiver_id != current_user.id:
        flash('无权操作。', 'danger')
        return redirect(url_for('user.friend_requests'))
    fr.status = 'rejected'
    db.session.commit()
    flash('已拒绝好友请求。', 'info')
    return redirect(url_for('user.friend_requests'))

@friend_bp.route('/remove/<int:user_id>', methods=['POST'])
@login_required
def remove_friend(user_id):
    user = User.query.get_or_404(user_id)
    if user in current_user.friends:
        current_user.friends.remove(user)
    if current_user in user.friends:
        user.friends.remove(current_user)
    db.session.commit()
    flash('已删除好友。', 'info')
    return redirect(url_for('user.profile', user_id=user_id))
