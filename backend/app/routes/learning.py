"""学习计划相关API"""
from flask import Blueprint, request, jsonify, g
from app import db
from app.models.word import Word
from app.models.learning_plan import LearningPlan
from app.models.review_log import ReviewLog
from app.utils.auth import login_required
from datetime import datetime
from sqlalchemy import and_

bp = Blueprint('learning', __name__, url_prefix='/api/learning')


@bp.route('/today', methods=['GET'])
@login_required
def get_today_review():
    """获取今日待复习单词"""
    try:
        # 查询当前用户需要复习的单词
        learning_plans = LearningPlan.query.filter(
            and_(
                LearningPlan.user_id == g.current_user.id,
                LearningPlan.next_review <= datetime.utcnow(),
                LearningPlan.is_mastered == False
            )
        ).all()
        
        words = []
        for plan in learning_plans:
            word = Word.query.get(plan.word_id)
            if word:
                word_dict = word.to_dict()
                word_dict['learning_plan'] = plan.to_dict()
                words.append(word_dict)
        
        return jsonify({
            'code': 200,
            'data': {
                'count': len(words),
                'words': words
            }
        })
    
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


@bp.route('/plan', methods=['GET'])
@login_required
def get_learning_plan():
    """获取学习计划概览"""
    try:
        # 当前用户的总单词数
        total_words = LearningPlan.query.filter_by(user_id=g.current_user.id).count()

        # 已掌握
        mastered = LearningPlan.query.filter_by(
            user_id=g.current_user.id,
            is_mastered=True
        ).count()

        # 学习中
        learning = LearningPlan.query.filter_by(
            user_id=g.current_user.id,
            is_mastered=False
        ).count()

        # 待复习
        to_review = LearningPlan.query.filter(
            and_(
                LearningPlan.user_id == g.current_user.id,
                LearningPlan.next_review <= datetime.utcnow(),
                LearningPlan.is_mastered == False
            )
        ).count()
        
        return jsonify({
            'code': 200,
            'data': {
                'total_words': total_words,
                'mastered': mastered,
                'learning': learning,
                'to_review': to_review
            }
        })
    
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


@bp.route('/review', methods=['POST'])
@login_required
def submit_review():
    """提交复习结果"""
    try:
        data = request.get_json()
        word_id = data.get('word_id')
        is_correct = data.get('is_correct')
        time_spent = data.get('time_spent', 0)

        if not word_id or is_correct is None:
            return jsonify({'code': 400, 'message': '参数不完整'}), 400

        # 获取当前用户的学习计划
        learning_plan = LearningPlan.query.filter_by(
            user_id=g.current_user.id,
            word_id=word_id
        ).first()

        if not learning_plan:
            return jsonify({'code': 404, 'message': '学习计划不存在'}), 404

        # 更新学习计划
        learning_plan.calculate_next_review(is_correct)

        # 创建复习记录
        review_log = ReviewLog(
            user_id=g.current_user.id,
            word_id=word_id,
            is_correct=is_correct,
            time_spent=time_spent
        )
        db.session.add(review_log)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '复习结果已提交',
            'data': learning_plan.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

