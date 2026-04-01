from app import create_app, db
from app.models.user import User, Hobby
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db.create_all()
    
    # 初始化爱好标签
    default_hobbies = [
        ('音乐', '艺术', '🎵'), ('电影', '娱乐', '🎬'), ('读书', '学习', '📚'),
        ('旅行', '生活', '✈️'), ('美食', '生活', '🍜'), ('运动', '健康', '🏃'),
        ('游戏', '娱乐', '🎮'), ('摄影', '艺术', '📷'), ('绘画', '艺术', '🎨'),
        ('编程', '技术', '💻'), ('健身', '健康', '💪'), ('宠物', '生活', '🐱'),
        ('瑜伽', '健康', '🧘'), ('舞蹈', '艺术', '💃'), ('烹饪', '生活', '👨‍🍳'),
        ('追剧', '娱乐', '📺'), ('骑行', '运动', '🚴'), ('爬山', '运动', '🏔️'),
        ('篮球', '运动', '🏀'), ('足球', '运动', '⚽'), ('汉服', '文化', '👘'),
        ('手工', '艺术', '✂️'), ('冥想', '健康', '🧠'), ('购物', '生活', '🛍️'),
    ]
    
    for name, category, icon in default_hobbies:
        if not Hobby.query.filter_by(name=name).first():
            h = Hobby(name=name, category=category, icon=icon)
            db.session.add(h)
    
    # 初始化管理员
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin', email='admin@friendplatform.com',
            password_hash=generate_password_hash('admin123'),
            nickname='超级管理员', is_admin=True, is_verified=True,
            gender='男', city='北京', province='北京', country='中国', age=28,
            bio='系统管理员',
        )
        db.session.add(admin)
    
    db.session.commit()
    print("OK: 数据库初始化完成！")
    print("OK: 已添加 24 个兴趣标签")
    print("OK: 管理员账号: admin / admin123")
