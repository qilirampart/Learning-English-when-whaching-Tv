"""应用入口文件"""
import os
from app import create_app

# 获取配置环境
config_name = os.getenv('FLASK_ENV', 'development')

# 创建应用实例
app = create_app(config_name)

if __name__ == '__main__':
    # 运行应用
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config.get('DEBUG', True)
    )

