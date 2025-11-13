"""认证工具"""
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from app.models import User


def generate_token(user_id, expires_in=86400):
    """
    生成 JWT token

    Args:
        user_id: 用户ID
        expires_in: 过期时间（秒），默认24小时

    Returns:
        token 字符串
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in),
        'iat': datetime.utcnow()
    }

    token = jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )

    return token


def verify_token(token):
    """
    验证 JWT token

    Args:
        token: JWT token 字符串

    Returns:
        user_id 或 None
    """
    try:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        return payload.get('user_id')
    except jwt.ExpiredSignatureError:
        # Token 已过期
        return None
    except jwt.InvalidTokenError:
        # Token 无效
        return None


def login_required(f):
    """
    登录验证装饰器

    使用方法:
        @bp.route('/protected')
        @login_required
        def protected_route():
            # 可以通过 g.current_user 访问当前用户
            return jsonify({'user': g.current_user.to_dict()})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 从请求头获取 token
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({
                'error': 'Missing authorization header',
                'message': '缺少认证信息'
            }), 401

        # 解析 Bearer token
        try:
            token_type, token = auth_header.split(' ')
            if token_type.lower() != 'bearer':
                return jsonify({
                    'error': 'Invalid token type',
                    'message': '无效的认证类型'
                }), 401
        except ValueError:
            return jsonify({
                'error': 'Invalid authorization header',
                'message': '无效的认证头格式'
            }), 401

        # 验证 token
        user_id = verify_token(token)
        if not user_id:
            return jsonify({
                'error': 'Invalid or expired token',
                'message': 'Token无效或已过期'
            }), 401

        # 获取用户
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'error': 'User not found',
                'message': '用户不存在'
            }), 401

        # 将用户信息存储到 flask.g 中
        from flask import g
        g.current_user = user

        return f(*args, **kwargs)

    return decorated_function


def optional_login(f):
    """
    可选登录装饰器（如果有token则验证，没有也允许访问）

    使用方法:
        @bp.route('/optional')
        @optional_login
        def optional_route():
            if hasattr(g, 'current_user'):
                return jsonify({'user': g.current_user.to_dict()})
            else:
                return jsonify({'user': None})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if auth_header:
            try:
                token_type, token = auth_header.split(' ')
                if token_type.lower() == 'bearer':
                    user_id = verify_token(token)
                    if user_id:
                        user = User.query.get(user_id)
                        if user:
                            from flask import g
                            g.current_user = user
            except (ValueError, AttributeError):
                pass

        return f(*args, **kwargs)

    return decorated_function
