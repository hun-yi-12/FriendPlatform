from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app.models.user import User, Post, Report, Hobby, FriendRequest
from app import db
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('需要管理员权限。', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    total_users = User.query.filter_by(is_admin=False).count()
    online_users = User.query.filter_by(online=True, is_admin=False).count()
    total_posts = Post.query.filter_by(is_deleted=False).count()
    pending_reports = Report.query.filter_by(status='pending').count()
    new_users_today = User.query.filter(
        User.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
    ).count()
    recent_users = User.query.filter_by(is_admin=False)\
        .order_by(User.created_at.desc()).limit(5).all()
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           online_users=online_users,
                           total_posts=total_posts,
                           pending_reports=pending_reports,
                           new_users_today=new_users_today,
                           recent_users=recent_users,
                           recent_posts=recent_posts)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    query = User.query.filter_by(is_admin=False)
    if search:
        query = query.filter(
            (User.username.ilike(f'%{search}%')) |
            (User.nickname.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )
    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/users.html', users=users, search=search)

@admin_bp.route('/user/<int:user_id>/ban', methods=['POST'])
@login_required
@admin_required
def ban_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_banned = True
    user.online = False
    db.session.commit()
    flash(f'已封禁用户 {user.username}。', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/user/<int:user_id>/unban', methods=['POST'])
@login_required
@admin_required
def unban_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_banned = False
    db.session.commit()
    flash(f'已解封用户 {user.username}。', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    Post.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    flash(f'已删除用户。', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/posts')
@login_required
@admin_required
def posts():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(is_deleted=False)\
        .order_by(Post.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/posts.html', posts=posts)

@admin_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.is_deleted = True
    db.session.commit()
    flash('已删除帖子。', 'success')
    return redirect(url_for('admin.posts'))

@admin_bp.route('/hobbies', methods=['GET', 'POST'])
@login_required
@admin_required
def hobbies():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip()
        icon = request.form.get('icon', '🎯').strip()
        if name and not Hobby.query.filter_by(name=name).first():
            h = Hobby(name=name, category=category, icon=icon)
            db.session.add(h)
            db.session.commit()
            flash(f'已添加爱好：{name}', 'success')
        else:
            flash('爱好名称已存在或为空。', 'warning')
    hobbies = Hobby.query.all()
    return render_template('admin/hobbies.html', hobbies=hobbies)

@admin_bp.route('/hobby/<int:hobby_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_hobby(hobby_id):
    h = Hobby.query.get_or_404(hobby_id)
    db.session.delete(h)
    db.session.commit()
    flash('已删除爱好标签。', 'success')
    return redirect(url_for('admin.hobbies'))

@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    reports = Report.query.filter_by(status='pending')\
        .order_by(Report.created_at.desc()).all()
    return render_template('admin/reports.html', reports=reports)

@admin_bp.route('/report/<int:report_id>/resolve', methods=['POST'])
@login_required
@admin_required
def resolve_report(report_id):
    r = Report.query.get_or_404(report_id)
    r.status = 'resolved'
    db.session.commit()
    flash('举报已处理。', 'success')
    return redirect(url_for('admin.reports'))
