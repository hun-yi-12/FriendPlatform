from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app.models.user import User
from app import db
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        if user and user.check_password(password):
            if user.is_banned:
                flash('账号已被封禁，请联系管理员。', 'danger')
                return redirect(url_for('auth.login'))
            user.online = True
            user.last_seen = datetime.utcnow()
            db.session.commit()
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash(f'欢迎回来，{user.nickname or user.username}！', 'success')
            return redirect(next_page or url_for('main.index'))
        flash('用户名或密码错误。', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')
        nickname = request.form.get('nickname', '').strip() or username
        gender = request.form.get('gender', '保密')
        age = request.form.get('age', 18, type=int)
        city = request.form.get('city', '').strip()
        province = request.form.get('province', '').strip()
        country = request.form.get('country', '中国').strip()

        if not username or not email or not password:
            flash('请填写完整信息。', 'warning')
            return redirect(url_for('auth.register'))
        if password != confirm:
            flash('两次密码不一致。', 'danger')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(username=username).first():
            flash('用户名已存在。', 'danger')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(email=email).first():
            flash('邮箱已注册。', 'danger')
            return redirect(url_for('auth.register'))

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            nickname=nickname,
            gender=gender,
            age=age,
            city=city,
            province=province,
            country=country,
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('注册成功！欢迎加入交友平台 🎉', 'success')
        return redirect(url_for('user.edit_profile'))
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    current_user.online = False
    db.session.commit()
    logout_user()
    flash('已退出登录。', 'info')
    return redirect(url_for('main.index'))
