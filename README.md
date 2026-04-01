# 缘来如此 - 交友平台

一个功能完整的 Python Flask 交友平台，支持同城、全国、全球三大交友范围。

## 功能模块

- 🏠 **首页** - 在线用户展示、最新动态、新朋友推荐
- 👥 **交友广场** - 同城/全国/全球三大范围 + 性别/爱好/习惯/目标多维筛选
- 🧠 **智能匹配** - 基于爱好、习惯、目标的算法推荐
- 💬 **心事广场** - 匿名发布心事，倾诉内心
- 💌 **实时聊天** - WebSocket 实时私信聊天
- 👤 **用户系统** - 注册/登录/个人主页/资料编辑
- 🤝 **好友系统** - 发送/接受/拒绝好友请求
- 🔧 **管理员后台** - 用户管理、内容审核、标签管理、举报处理

## 快速启动

```bash
cd FriendPlatform

# 安装依赖
pip install -r requirements.txt

# 初始化数据库（首次运行）
python init_db.py

# 启动项目
python run.py
```

访问 http://127.0.0.1:5000

## 默认账号

| 账号 | 密码 | 权限 |
|------|------|------|
| admin | admin123 | 管理员 |

管理员后台：http://127.0.0.1:5000/admin

## 技术栈

- **后端**: Flask + Flask-SQLAlchemy + Flask-Login + Flask-SocketIO
- **数据库**: SQLite
- **前端**: Bootstrap 5 + Font Awesome
- **实时通信**: Socket.IO
