from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
import os

db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'friendplatform-secret-key-2026'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///friend_platform.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'img', 'avatars')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录！'
    login_manager.login_message_category = 'warning'
    
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.user import user_bp
    from app.routes.admin import admin_bp
    from app.routes.friend import friend_bp
    from app.routes.chat import chat_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(friend_bp, url_prefix='/friend')
    app.register_blueprint(chat_bp, url_prefix='/chat')
    
    with app.app_context():
        db.create_all()
        from app.models.user import User
        # 创建默认管理员
        if not User.query.filter_by(username='admin').first():
            from werkzeug.security import generate_password_hash
            admin = User(
                username='admin',
                email='admin@friendplatform.com',
                password_hash=generate_password_hash('admin123'),
                nickname='超级管理员',
                is_admin=True,
                is_verified=True,
                gender='男',
                city='北京',
                province='北京',
                country='中国',
                age=28,
                bio='系统管理员',
            )
            db.session.add(admin)
            db.session.commit()
    
    return app
