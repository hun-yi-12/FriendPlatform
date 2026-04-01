from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    print("=" * 50)
    print("  缘来如此 - 交友平台启动中...")
    print("  访问地址: http://127.0.0.1:5000")
    print("  管理员账号: admin / admin123")
    print("=" * 50)
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
