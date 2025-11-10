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
    from config import config
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

