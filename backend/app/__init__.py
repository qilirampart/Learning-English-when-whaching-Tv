"""Flask应用工厂"""
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# 初始化数据库
db = SQLAlchemy()


def create_app(config_name='default'):
    """创建Flask应用实例"""
    app = Flask(__name__)

    # 加载配置
    import sys
    import os

    # 获取backend目录的绝对路径
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 确保backend目录在sys.path中
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    # 导入config模块
    try:
        from config import config
    except ImportError:
        # 如果仍然无法导入，尝试直接从backend目录导入
        config_path = os.path.join(backend_dir, 'config.py')
        if os.path.exists(config_path):
            import importlib.util
            spec = importlib.util.spec_from_file_location("config", config_path)
            config_module = importlib.util.module_from_spec(spec)
            sys.modules["config"] = config_module
            spec.loader.exec_module(config_module)
            config = config_module.config
        else:
            raise ImportError(f"Cannot find config.py in {backend_dir}")

    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # 注册蓝图
    from app.routes import words, learning, statistics
    app.register_blueprint(words.bp)
    app.register_blueprint(learning.bp)
    app.register_blueprint(statistics.bp)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app

