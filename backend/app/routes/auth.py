"""认证路由"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from app.models import User
from app.utils.auth import generate_token, login_required
import re

bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def validate_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """
    验证密码强度
    要求: 至少6个字符
    """
    return len(password) >= 6


@bp.route('/register', methods=['POST'])
def register():
    """
    用户注册

    请求体:
    {
        "username": "用户名",
        "email": "邮箱",
        "password": "密码"
    }

    返回:
    {
        "message": "注册成功",
        "user": {...},
        "token": "JWT token"
    }
    """
    try:
        data = request.get_json()

        # 验证必填字段
        if not data or not all(k in data for k in ('username', 'email', 'password')):
            return jsonify({
                'error': 'Missing required fields',
                'message': '缺少必填字段'
            }), 400

        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']

        # 验证用户名
        if len(username) < 3 or len(username) > 80:
            return jsonify({
                'error': 'Invalid username',
                'message': '用户名长度必须在3-80个字符之间'
            }), 400

        # 验证邮箱
        if not validate_email(email):
            return jsonify({
                'error': 'Invalid email',
                'message': '邮箱格式不正确'
            }), 400

        # 验证密码
        if not validate_password(password):
            return jsonify({
                'error': 'Invalid password',
                'message': '密码至少需要6个字符'
            }), 400

        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({
                'error': 'Username exists',
                'message': '用户名已存在'
            }), 409

        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            return jsonify({
                'error': 'Email exists',
                'message': '邮箱已被注册'
            }), 409

        # 创建新用户
        user = User(username=username, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        # 生成 token
        token = generate_token(user.id)

        return jsonify({
            'message': '注册成功',
            'user': user.to_dict(),
            'token': token
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Registration failed',
            'message': f'注册失败: {str(e)}'
        }), 500


@bp.route('/login', methods=['POST'])
def login():
    """
    用户登录

    请求体:
    {
        "username": "用户名或邮箱",
        "password": "密码"
    }

    返回:
    {
        "message": "登录成功",
        "user": {...},
        "token": "JWT token"
    }
    """
    try:
        data = request.get_json()

        # 验证必填字段
        if not data or not all(k in data for k in ('username', 'password')):
            return jsonify({
                'error': 'Missing required fields',
                'message': '缺少必填字段'
            }), 400

        username = data['username'].strip()
        password = data['password']

        # 查找用户（支持用户名或邮箱登录）
        user = User.query.filter(
            (User.username == username) | (User.email == username.lower())
        ).first()

        # 验证用户和密码
        if not user or not user.check_password(password):
            return jsonify({
                'error': 'Invalid credentials',
                'message': '用户名或密码错误'
            }), 401

        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        db.session.commit()

        # 生成 token
        token = generate_token(user.id)

        return jsonify({
            'message': '登录成功',
            'user': user.to_dict(),
            'token': token
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Login failed',
            'message': f'登录失败: {str(e)}'
        }), 500


@bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """
    获取当前用户信息

    需要认证

    返回:
    {
        "user": {...}
    }
    """
    from flask import g
    return jsonify({
        'user': g.current_user.to_dict()
    }), 200


@bp.route('/refresh', methods=['POST'])
@login_required
def refresh_token():
    """
    刷新 token

    需要认证

    返回:
    {
        "token": "新的 JWT token"
    }
    """
    from flask import g
    token = generate_token(g.current_user.id)

    return jsonify({
        'message': 'Token刷新成功',
        'token': token
    }), 200
