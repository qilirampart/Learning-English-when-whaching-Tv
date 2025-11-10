"""单词相关API"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.word import Word
from app.models.query_log import QueryLog
from app.models.learning_plan import LearningPlan
from app.services.translation_service import TranslationService
from sqlalchemy import desc, func
import json

bp = Blueprint('words', __name__, url_prefix='/api/words')
translation_service = TranslationService()


@bp.route('/query', methods=['POST'])
def query_word():
    """查询单词并自动记录"""
    try:
        data = request.get_json()
        word_text = data.get('word', '').strip().lower()
        
        if not word_text:
            return jsonify({'code': 400, 'message': '单词不能为空'}), 400
        
        # 查询数据库中是否已存在该单词
        word = Word.query.filter_by(word=word_text).first()
        
        if not word:
            # 如果不存在，调用翻译API获取释义
            translation_result = translation_service.translate(word_text)
            
            if not translation_result:
                return jsonify({'code': 500, 'message': '翻译服务暂时不可用'}), 500
            
            # 创建新单词记录
            word = Word(
                word=word_text,
                phonetic=translation_result.get('phonetic', ''),
                translation=translation_result.get('translation', ''),
                definition=translation_result.get('definition', ''),
                examples=json.dumps(translation_result.get('examples', []), ensure_ascii=False)
            )
            db.session.add(word)
            db.session.flush()  # 获取word.id
            
            # 创建学习计划
            learning_plan = LearningPlan(word_id=word.id)
            db.session.add(learning_plan)
        
        # 创建查询记录
        query_log = QueryLog(
            word_id=word.id,
            tv_show=data.get('tv_show', ''),
            season_episode=data.get('season_episode', ''),
            context_note=data.get('context_note', '')
        )
        db.session.add(query_log)
        db.session.commit()
        
        # 返回结果
        result = word.to_dict()
        result['last_query'] = query_log.query_time.isoformat()
        
        return jsonify({'code': 200, 'data': result})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


@bp.route('/search', methods=['GET'])
def search_words():
    """搜索历史查询过的单词"""
    try:
        keyword = request.args.get('keyword', '').strip()
        
        if not keyword:
            return jsonify({'code': 400, 'message': '关键词不能为空'}), 400
        
        words = Word.query.filter(Word.word.like(f'%{keyword}%')).limit(20).all()
        
        return jsonify({
            'code': 200,
            'data': [word.to_dict() for word in words]
        })
    
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


@bp.route('/<int:word_id>', methods=['GET'])
def get_word_detail(word_id):
    """获取单词详情（含查询历史）"""
    try:
        word = Word.query.get(word_id)
        
        if not word:
            return jsonify({'code': 404, 'message': '单词不存在'}), 404
        
        # 获取查询历史
        query_logs = QueryLog.query.filter_by(word_id=word_id).order_by(desc(QueryLog.query_time)).all()
        
        # 获取学习计划
        learning_plan = LearningPlan.query.filter_by(word_id=word_id).first()
        
        result = word.to_dict()
        result['query_logs'] = [log.to_dict() for log in query_logs]
        result['learning_plan'] = learning_plan.to_dict() if learning_plan else None
        
        return jsonify({'code': 200, 'data': result})
    
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


@bp.route('/list', methods=['GET'])
def get_words_list():
    """获取所有查询过的单词列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        order_by = request.args.get('order_by', 'time')  # time/frequency/mastery
        filter_show = request.args.get('filter_show', '')
        mastery_level = request.args.get('mastery_level', type=int)
        
        # 构建查询
        query = Word.query
        
        # 按剧集筛选
        if filter_show:
            query = query.join(QueryLog).filter(QueryLog.tv_show.like(f'%{filter_show}%'))
        
        # 按掌握程度筛选
        if mastery_level is not None:
            query = query.join(LearningPlan).filter(LearningPlan.mastery_level == mastery_level)
        
        # 排序
        if order_by == 'frequency':
            # 按查询频率排序
            query = query.outerjoin(QueryLog).group_by(Word.id).order_by(desc(func.count(QueryLog.id)))
        elif order_by == 'mastery':
            # 按掌握程度排序
            query = query.outerjoin(LearningPlan).order_by(desc(LearningPlan.mastery_level))
        else:
            # 默认按时间排序
            query = query.order_by(desc(Word.created_at))
        
        # 分页
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        
        # 构建返回数据
        items = []
        for word in pagination.items:
            word_dict = word.to_dict()
            
            # 添加剧集信息
            tv_shows = db.session.query(QueryLog.tv_show).filter(
                QueryLog.word_id == word.id,
                QueryLog.tv_show != ''
            ).distinct().all()
            word_dict['tv_shows'] = [show[0] for show in tv_shows]
            
            # 添加掌握程度
            learning_plan = LearningPlan.query.filter_by(word_id=word.id).first()
            word_dict['mastery_level'] = learning_plan.mastery_level if learning_plan else 0
            
            # 最后查询时间
            last_query = QueryLog.query.filter_by(word_id=word.id).order_by(desc(QueryLog.query_time)).first()
            word_dict['last_query'] = last_query.query_time.isoformat() if last_query else None
            
            items.append(word_dict)
        
        return jsonify({
            'code': 200,
            'data': {
                'total': pagination.total,
                'page': page,
                'page_size': page_size,
                'items': items
            }
        })
    
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

