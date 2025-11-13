"""统计相关API"""
from flask import Blueprint, jsonify, g
from app import db
from app.models.word import Word
from app.models.query_log import QueryLog
from app.models.learning_plan import LearningPlan
from app.utils.auth import login_required
from datetime import datetime, timedelta
from sqlalchemy import func, and_

bp = Blueprint('statistics', __name__, url_prefix='/api/statistics')


@bp.route('/overview', methods=['GET'])
@login_required
def get_overview():
    """获取学习统计概览"""
    try:
        # 当前用户的总单词数
        total_words = LearningPlan.query.filter_by(user_id=g.current_user.id).count()

        # 今日查询数
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_queries = QueryLog.query.filter(
            QueryLog.user_id == g.current_user.id,
            QueryLog.query_time >= today_start
        ).count()

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

        # 最近7天的查询趋势
        weekly_trend = []
        for i in range(6, -1, -1):
            day_start = (datetime.utcnow() - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            count = QueryLog.query.filter(
                and_(
                    QueryLog.user_id == g.current_user.id,
                    QueryLog.query_time >= day_start,
                    QueryLog.query_time < day_end
                )
            ).count()
            weekly_trend.append(count)
        
        return jsonify({
            'code': 200,
            'data': {
                'total_words': total_words,
                'today_queries': today_queries,
                'mastered': mastered,
                'learning': learning,
                'to_review': to_review,
                'weekly_trend': weekly_trend
            }
        })
    
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


@bp.route('/tv_shows', methods=['GET'])
@login_required
def get_tv_show_stats():
    """获取剧集统计"""
    try:
        # 查询当前用户每个剧集的单词数量
        results = db.session.query(
            QueryLog.tv_show,
            func.count(func.distinct(QueryLog.word_id)).label('word_count')
        ).filter(
            QueryLog.user_id == g.current_user.id,
            QueryLog.tv_show != ''
        ).group_by(
            QueryLog.tv_show
        ).order_by(
            func.count(func.distinct(QueryLog.word_id)).desc()
        ).limit(10).all()
        
        tv_shows = [
            {
                'tv_show': result.tv_show,
                'word_count': result.word_count
            }
            for result in results
        ]
        
        return jsonify({
            'code': 200,
            'data': tv_shows
        })
    
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

