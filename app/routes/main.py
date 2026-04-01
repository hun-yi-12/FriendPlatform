from flask import Blueprint, render_template, request
from flask_login import current_user
from app.models.user import User, Post, Hobby
from app import db
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # 最新动态
    recent_posts = Post.query.filter_by(is_deleted=False, post_type='normal')\
        .order_by(Post.created_at.desc()).limit(6).all()
    # 在线用户
    online_users = User.query.filter_by(online=True, is_banned=False).limit(8).all()
    # 新注册用户
    new_users = User.query.filter_by(is_banned=False)\
        .order_by(User.created_at.desc()).limit(8).all()
    total_users = User.query.filter_by(is_banned=False).count()
    return render_template('main/index.html',
                           recent_posts=recent_posts,
                           online_users=online_users,
                           new_users=new_users,
                           total_users=total_users)

@main_bp.route('/explore')
def explore():
    scope = request.args.get('scope', 'all')   # city / national / global
    gender = request.args.get('gender', '')
    hobby_id = request.args.get('hobby', '')
    habit = request.args.get('habit', '')
    goal = request.args.get('goal', '')
    page = request.args.get('page', 1, type=int)

    query = User.query.filter_by(is_banned=False, is_admin=False)

    if scope == 'city' and current_user.is_authenticated:
        query = query.filter_by(city=current_user.city)
    elif scope == 'national' and current_user.is_authenticated:
        query = query.filter_by(country=current_user.country)
    # global: 不过滤

    if gender:
        query = query.filter_by(gender=gender)
    if habit:
        query = query.filter_by(habit_sleep=habit)
    if goal:
        query = query.filter_by(relationship_goal=goal)
    if hobby_id:
        hobby = Hobby.query.get(hobby_id)
        if hobby:
            query = query.filter(User.hobbies.contains(hobby))

    users = query.order_by(User.last_seen.desc()).paginate(page=page, per_page=12)
    hobbies = Hobby.query.all()
    return render_template('main/explore.html', users=users, scope=scope,
                           hobbies=hobbies, gender=gender,
                           selected_hobby=hobby_id, habit=habit, goal=goal)

@main_bp.route('/secrets')
def secrets():
    """心事广场"""
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(post_type='secret', is_deleted=False)\
        .order_by(Post.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('main/secrets.html', posts=posts)
