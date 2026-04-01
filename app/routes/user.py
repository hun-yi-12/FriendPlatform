from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.models.user import User, Post, FriendRequest, Hobby, Message
from app import db
from datetime import datetime
import os
from werkzeug.utils import secure_filename

user_bp = Blueprint('user', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user_bp.route('/profile/<int:user_id>')
def profile(user_id):
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user_id, is_deleted=False, post_type='normal')\
        .order_by(Post.created_at.desc()).limit(10).all()
    is_friend = False
    pending_request = None
    if current_user.is_authenticated and current_user.id != user_id:
        is_friend = current_user.is_friend(user)
        pending_request = FriendRequest.query.filter_by(
            sender_id=current_user.id, receiver_id=user_id, status='pending').first()
    return render_template('user/profile.html', user=user, posts=posts,
                           is_friend=is_friend, pending_request=pending_request)

@user_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    hobbies = Hobby.query.all()
    if request.method == 'POST':
        current_user.nickname = request.form.get('nickname', '').strip()
        current_user.gender = request.form.get('gender', '保密')
        current_user.age = request.form.get('age', 18, type=int)
        current_user.city = request.form.get('city', '').strip()
        current_user.province = request.form.get('province', '').strip()
        current_user.country = request.form.get('country', '中国').strip()
        current_user.bio = request.form.get('bio', '').strip()
        current_user.habit_sleep = request.form.get('habit_sleep', '')
        current_user.habit_diet = request.form.get('habit_diet', '')
        current_user.habit_exercise = request.form.get('habit_exercise', '')
        current_user.life_goal = request.form.get('life_goal', '').strip()
        current_user.relationship_goal = request.form.get('relationship_goal', '')

        # 爱好
        hobby_ids = request.form.getlist('hobbies')
        selected_hobbies = Hobby.query.filter(Hobby.id.in_(hobby_ids)).all()
        current_user.hobbies = selected_hobbies

        # 头像上传
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename and allowed_file(file.filename):
                filename = f"user_{current_user.id}_{secure_filename(file.filename)}"
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                current_user.avatar = filename

        db.session.commit()
        flash('资料更新成功！', 'success')
        return redirect(url_for('user.profile', user_id=current_user.id))
    return render_template('user/edit_profile.html', hobbies=hobbies)

@user_bp.route('/post/new', methods=['POST'])
@login_required
def new_post():
    content = request.form.get('content', '').strip()
    post_type = request.form.get('post_type', 'normal')
    if not content:
        flash('内容不能为空。', 'warning')
        return redirect(url_for('user.profile', user_id=current_user.id))
    post = Post(user_id=current_user.id, content=content, post_type=post_type)
    db.session.add(post)
    db.session.commit()
    flash('发布成功！', 'success')
    if post_type == 'secret':
        return redirect(url_for('main.secrets'))
    return redirect(url_for('user.profile', user_id=current_user.id))

@user_bp.route('/requests')
@login_required
def friend_requests():
    received = FriendRequest.query.filter_by(
        receiver_id=current_user.id, status='pending').all()
    sent = FriendRequest.query.filter_by(
        sender_id=current_user.id, status='pending').all()
    return render_template('user/friend_requests.html', received=received, sent=sent)

@user_bp.route('/match')
@login_required
def match():
    """智能匹配推荐"""
    candidates = User.query.filter(
        User.id != current_user.id,
        User.is_banned == False,
        User.is_admin == False
    ).all()
    
    scored = []
    for u in candidates:
        score = 0
        # 爱好匹配
        common_hobbies = set(h.id for h in current_user.hobbies) & set(h.id for h in u.hobbies)
        score += len(common_hobbies) * 20
        # 习惯匹配
        if current_user.habit_sleep and current_user.habit_sleep == u.habit_sleep:
            score += 15
        if current_user.habit_diet and current_user.habit_diet == u.habit_diet:
            score += 10
        if current_user.habit_exercise and current_user.habit_exercise == u.habit_exercise:
            score += 10
        # 目标匹配
        if current_user.relationship_goal and current_user.relationship_goal == u.relationship_goal:
            score += 25
        if current_user.life_goal and current_user.life_goal == u.life_goal:
            score += 15
        # 同城加分
        if current_user.city and current_user.city == u.city:
            score += 10
        if score > 0:
            scored.append((u, score, list(common_hobbies)))
    
    scored.sort(key=lambda x: x[1], reverse=True)
    return render_template('user/match.html', scored=scored[:20])
