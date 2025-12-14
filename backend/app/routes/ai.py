"""
AI 智能助手路由
"""
from flask import Blueprint, request, jsonify
from app.services.ai_service import ai_service

bp = Blueprint('ai', __name__, url_prefix='/api/ai')


@bp.route('/usage', methods=['POST'])
def generate_usage():
    """
    生成单词用法解析

    Request JSON:
    {
        "word": "bastard",
        "tv_show": "老友记"  // 可选
    }

    Response:
    {
        "code": 200,
        "data": {
            "word": "bastard",
            "tv_show": "老友记",
            "content": "详细的用法解析..."
        }
    }
    """
    try:
        data = request.get_json()

        # 参数验证
        if not data or 'word' not in data:
            return jsonify({
                "code": 400,
                "message": "缺少必要参数：word"
            }), 400

        word = data['word'].strip()
        tv_show = data.get('tv_show', '').strip() if data.get('tv_show') else None

        if not word:
            return jsonify({
                "code": 400,
                "message": "单词不能为空"
            }), 400

        # 调用 AI 服务
        result = ai_service.generate_word_usage(word, tv_show)

        # 添加详细日志
        print(f"[AI 用法生成] 单词: {word}, 剧名: {tv_show}")
        print(f"[AI 用法生成] 返回结果: success={result.get('success')}, content长度={len(result.get('content', ''))}")
        if result.get('content'):
            print(f"[AI 用法生成] 内容预览: {result.get('content')[:100]}...")
        else:
            print(f"[AI 用法生成] ⚠️ 警告：content 字段为空！完整结果: {result}")

        if result['success']:
            # 二次验证 content 是否有效
            if not result.get('content') or len(result.get('content', '').strip()) == 0:
                print(f"[AI 用法生成] ❌ 错误：AI 返回 success=True 但 content 为空")
                return jsonify({
                    "code": 500,
                    "message": "AI 生成内容为空，请重试",
                    "error": "Empty content from AI"
                }), 500

            return jsonify({
                "code": 200,
                "data": result
            })
        else:
            return jsonify({
                "code": 500,
                "message": result.get('message', 'AI 服务调用失败'),
                "error": result.get('error')
            }), 500

    except Exception as e:
        return jsonify({
            "code": 500,
            "message": "服务器错误",
            "error": str(e)
        }), 500


@bp.route('/examples', methods=['POST'])
def generate_examples():
    """
    生成单词例句

    Request JSON:
    {
        "word": "hello",
        "count": 5  // 可选，默认 5
    }

    Response:
    {
        "code": 200,
        "data": {
            "word": "hello",
            "examples": [...]
        }
    }
    """
    try:
        data = request.get_json()

        if not data or 'word' not in data:
            return jsonify({
                "code": 400,
                "message": "缺少必要参数：word"
            }), 400

        word = data['word'].strip()
        count = data.get('count', 5)

        if not word:
            return jsonify({
                "code": 400,
                "message": "单词不能为空"
            }), 400

        # 调用 AI 服务
        result = ai_service.generate_examples(word, count)

        if result['success']:
            return jsonify({
                "code": 200,
                "data": result
            })
        else:
            return jsonify({
                "code": 500,
                "message": result.get('message', 'AI 服务调用失败'),
                "error": result.get('error')
            }), 500

    except Exception as e:
        return jsonify({
            "code": 500,
            "message": "服务器错误",
            "error": str(e)
        }), 500


@bp.route('/difference', methods=['POST'])
def explain_difference():
    """
    解释近义词差异

    Request JSON:
    {
        "words": ["see", "look", "watch"]
    }

    Response:
    {
        "code": 200,
        "data": {
            "words": ["see", "look", "watch"],
            "content": "差异解释..."
        }
    }
    """
    try:
        data = request.get_json()

        if not data or 'words' not in data:
            return jsonify({
                "code": 400,
                "message": "缺少必要参数：words"
            }), 400

        words = data['words']

        if not isinstance(words, list) or len(words) < 2:
            return jsonify({
                "code": 400,
                "message": "需要至少 2 个单词进行对比"
            }), 400

        # 调用 AI 服务
        result = ai_service.explain_difference(words)

        if result['success']:
            return jsonify({
                "code": 200,
                "data": result
            })
        else:
            return jsonify({
                "code": 500,
                "message": result.get('message', 'AI 服务调用失败'),
                "error": result.get('error')
            }), 500

    except Exception as e:
        return jsonify({
            "code": 500,
            "message": "服务器错误",
            "error": str(e)
        }), 500


@bp.route('/memory-tips', methods=['POST'])
def generate_memory_tips():
    """
    生成记忆口诀

    Request JSON:
    {
        "word": "hello"
    }

    Response:
    {
        "code": 200,
        "data": {
            "word": "hello",
            "content": "记忆技巧..."
        }
    }
    """
    try:
        data = request.get_json()

        if not data or 'word' not in data:
            return jsonify({
                "code": 400,
                "message": "缺少必要参数：word"
            }), 400

        word = data['word'].strip()

        if not word:
            return jsonify({
                "code": 400,
                "message": "单词不能为空"
            }), 400

        # 调用 AI 服务
        result = ai_service.generate_memory_tips(word)

        if result['success']:
            return jsonify({
                "code": 200,
                "data": result
            })
        else:
            return jsonify({
                "code": 500,
                "message": result.get('message', 'AI 服务调用失败'),
                "error": result.get('error')
            }), 500

    except Exception as e:
        return jsonify({
            "code": 500,
            "message": "服务器错误",
            "error": str(e)
        }), 500
