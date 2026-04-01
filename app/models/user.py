from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# 用户爱好关联表
user_hobbies = db.Table('user_hobbies',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('hobby_id', db.Integer, db.ForeignKey('hobby.id'))
)

# 好友关系表
friendships = db.Table('friendships',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('friend_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    nickname = db.Column(db.String(80), default='')
    avatar = db.Column(db.String(200), default='default.png')
    gender = db.Column(db.String(10), default='保密')
    age = db.Column(db.Integer, default=18)
    bio = db.Column(db.Text, default='')
    city = db.Column(db.String(50), default='')
    province = db.Column(db.String(50), default='')
    country = db.Column(db.String(50), default='中国')
    
    # 生活方式标签
    habit_sleep = db.Column(db.String(20), default='')   # 作息习惯
    habit_diet = db.Column(db.String(20), default='')    # 饮食习惯
    habit_exercise = db.Column(db.String(20), default='')# 运动习惯
    
    # 目标
    life_goal = db.Column(db.String(100), default='')    # 人生目标
    relationship_goal = db.Column(db.String(50), default='') # 交友目标
    
    # 状态
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_banned = db.Column(db.Boolean, default=False)
    online = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联
    hobbies = db.relationship('Hobby', secondary=user_hobbies, backref='users')
    friends = db.relationship('User', secondary=friendships,
                              primaryjoin=id==friendships.c.user_id,
                              secondaryjoin=id==friendships.c.friend_id)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy='dynamic')
    friend_requests_sent = db.relationship('FriendRequest', foreign_keys='FriendRequest.sender_id', backref='sender', lazy='dynamic')
    friend_requests_received = db.relationship('FriendRequest', foreign_keys='FriendRequest.receiver_id', backref='receiver', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_friend(self, user):
        return user in self.friends
    
    def __repr__(self):
        return f'<User {self.username}>'

class Hobby(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(30), default='')
    icon = db.Column(db.String(50), default='🎯')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    post_type = db.Column(db.String(20), default='normal')  # normal / secret (心事)
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FriendRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(200), default='')
    status = db.Column(db.String(20), default='pending')  # pending/accepted/rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reported_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    reported_post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    reason = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
