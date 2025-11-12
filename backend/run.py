"""应用入口文件"""
import os
from app import create_app

# 获取配置环境
config_name = os.getenv('FLASK_ENV', 'development')

# 创建应用实例
app = create_app(config_name)

if __name__ == '__main__':
    # 运行应用
    # 生产环境使用环境变量中的PORT，开发环境使用5000
    port = int(os.getenv('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config.get('DEBUG', True)
    )

