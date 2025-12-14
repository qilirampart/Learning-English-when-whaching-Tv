"""单词相关API"""
from flask import Blueprint, request, jsonify, g, send_file
from app import db
from app.models.word import Word
from app.models.query_log import QueryLog
from app.models.learning_plan import LearningPlan
from app.services.translation_service import TranslationService
from app.services.export_service import ExportService
from app.utils.auth import login_required
from sqlalchemy import desc, func
from datetime import datetime
import json

bp = Blueprint('words', __name__, url_prefix='/api/words')
translation_service = TranslationService()
export_service = ExportService()


@bp.route('/query', methods=['POST'])
@login_required
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
            
        # 检查当前用户是否已有该单词的学习计划
        learning_plan = LearningPlan.query.filter_by(
            user_id=g.current_user.id,
            word_id=word.id
        ).first()

        if not learning_plan:
            # 创建学习计划
            learning_plan = LearningPlan(
                user_id=g.current_user.id,
                word_id=word.id
            )
            db.session.add(learning_plan)

        # 创建查询记录
        query_log = QueryLog(
            user_id=g.current_user.id,
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
@login_required
def search_words():
    """搜索历史查询过的单词"""
    try:
        keyword = request.args.get('keyword', '').strip()

        if not keyword:
            return jsonify({'code': 400, 'message': '关键词不能为空'}), 400

        # 只搜索当前用户查询过的单词
        words = Word.query.join(QueryLog).filter(
            QueryLog.user_id == g.current_user.id,
            Word.word.like(f'%{keyword}%')
        ).distinct().limit(20).all()
        
        return jsonify({
            'code': 200,
            'data': [word.to_dict() for word in words]
        })
    
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


@bp.route('/<int:word_id>', methods=['GET'])
@login_required
def get_word_detail(word_id):
    """获取单词详情（含查询历史）"""
    try:
        word = Word.query.get(word_id)
        
        if not word:
            return jsonify({'code': 404, 'message': '单词不存在'}), 404
        
        # 获取当前用户的查询历史
        query_logs = QueryLog.query.filter_by(
            user_id=g.current_user.id,
            word_id=word_id
        ).order_by(desc(QueryLog.query_time)).all()

        # 获取当前用户的学习计划
        learning_plan = LearningPlan.query.filter_by(
            user_id=g.current_user.id,
            word_id=word_id
        ).first()
        
        result = word.to_dict()
        result['query_logs'] = [log.to_dict() for log in query_logs]
        result['learning_plan'] = learning_plan.to_dict() if learning_plan else None
        
        return jsonify({'code': 200, 'data': result})
    
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


@bp.route('/list', methods=['GET'])
@login_required
def get_words_list():
    """获取所有查询过的单词列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        order_by = request.args.get('order_by', 'time')  # time/frequency/mastery
        filter_show = request.args.get('filter_show', '')
        mastery_level = request.args.get('mastery_level', type=int)
        
        # 构建查询 - 只查询当前用户的单词
        query = Word.query.join(QueryLog).filter(QueryLog.user_id == g.current_user.id)

        # 按剧集筛选
        if filter_show:
            query = query.filter(QueryLog.tv_show.like(f'%{filter_show}%'))

        # 按掌握程度筛选
        if mastery_level is not None:
            query = query.join(LearningPlan).filter(
                LearningPlan.user_id == g.current_user.id,
                LearningPlan.mastery_level == mastery_level
            )
        
        # 去重（因为一个单词可能有多条查询记录）
        query = query.distinct()

        # 排序
        if order_by == 'frequency':
            # 按查询频率排序 - 统计当前用户的查询次数
            query = query.group_by(Word.id).order_by(desc(func.count(QueryLog.id)))
        elif order_by == 'mastery':
            # 按掌握程度排序
            query = query.outerjoin(LearningPlan,
                (LearningPlan.word_id == Word.id) & (LearningPlan.user_id == g.current_user.id)
            ).order_by(desc(LearningPlan.mastery_level))
        else:
            # 默认按最后查询时间排序
            query = query.order_by(desc(QueryLog.query_time))
        
        # 分页
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        
        # 构建返回数据
        items = []
        for word in pagination.items:
            word_dict = word.to_dict()
            
            # 添加当前用户的剧集信息
            tv_shows = db.session.query(QueryLog.tv_show).filter(
                QueryLog.user_id == g.current_user.id,
                QueryLog.word_id == word.id,
                QueryLog.tv_show != ''
            ).distinct().all()
            word_dict['tv_shows'] = [show[0] for show in tv_shows]

            # 添加当前用户的掌握程度
            learning_plan = LearningPlan.query.filter_by(
                user_id=g.current_user.id,
                word_id=word.id
            ).first()
            word_dict['mastery_level'] = learning_plan.mastery_level if learning_plan else 0

            # 当前用户的最后查询时间
            last_query = QueryLog.query.filter_by(
                user_id=g.current_user.id,
                word_id=word.id
            ).order_by(desc(QueryLog.query_time)).first()
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


@bp.route('/export', methods=['GET'])
@login_required
def export_words():
    """导出单词本"""
    try:
        # 获取导出格式
        export_format = request.args.get('format', 'excel').lower()

        if export_format not in ['excel', 'pdf']:
            return jsonify({'code': 400, 'message': '不支持的导出格式，仅支持 excel 或 pdf'}), 400

        # 检查依赖
        dependencies = export_service.check_dependencies()

        if export_format == 'excel' and not dependencies['excel']:
            return jsonify({
                'code': 500,
                'message': 'Excel 导出功能未配置，请安装 openpyxl 库'
            }), 500

        if export_format == 'pdf' and not dependencies['pdf']:
            return jsonify({
                'code': 500,
                'message': 'PDF 导出功能未配置，请安装 reportlab 库'
            }), 500

        # 获取当前用户的所有单词
        words_query = Word.query.join(QueryLog).filter(
            QueryLog.user_id == g.current_user.id
        ).distinct()

        # 按最后查询时间排序
        words_query = words_query.order_by(desc(QueryLog.query_time))

        words = words_query.all()

        if not words:
            return jsonify({'code': 400, 'message': '您还没有查询过任何单词'}), 400

        # 构建导出数据
        export_data = []
        for word in words:
            word_dict = word.to_dict()

            # 添加用户相关数据
            # 掌握度
            learning_plan = LearningPlan.query.filter_by(
                user_id=g.current_user.id,
                word_id=word.id
            ).first()
            word_dict['mastery_level'] = learning_plan.mastery_level if learning_plan else 0

            # 查询次数（当前用户）
            query_count = QueryLog.query.filter_by(
                user_id=g.current_user.id,
                word_id=word.id
            ).count()
            word_dict['query_count'] = query_count

            # 最后查询时间
            last_query = QueryLog.query.filter_by(
                user_id=g.current_user.id,
                word_id=word.id
            ).order_by(desc(QueryLog.query_time)).first()
            word_dict['last_query'] = last_query.query_time.isoformat() if last_query else None

            export_data.append(word_dict)

        # 用户信息
        user_info = {
            'username': g.current_user.username,
            'email': g.current_user.email
        }

        # 导出文件
        if export_format == 'excel':
            output = export_service.export_to_excel(export_data, user_info)
            filename = f"单词本_{g.current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        else:  # pdf
            output = export_service.export_to_pdf(export_data, user_info)
            filename = f"单词本_{g.current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            mimetype = 'application/pdf'

        return send_file(
            output,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )

    except ImportError as e:
        return jsonify({
            'code': 500,
            'message': f'导出功能未配置: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({'code': 500, 'message': f'导出失败: {str(e)}'}), 500


@bp.route('/<int:word_id>', methods=['PUT'])
@login_required
def update_word(word_id):
    """更新单词信息（例句等）"""
    try:
        word = Word.query.get(word_id)

        if not word:
            return jsonify({'code': 404, 'message': '单词不存在'}), 404

        data = request.get_json()

        # 更新例句
        if 'examples' in data:
            word.examples = data['examples']

        # 更新其他字段（如果需要）
        if 'phonetic' in data:
            word.phonetic = data['phonetic']
        if 'translation' in data:
            word.translation = data['translation']
        if 'definition' in data:
            word.definition = data['definition']

        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': word.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'更新失败: {str(e)}'}), 500


@bp.route('/export/check', methods=['GET'])
@login_required
def check_export_availability():
    """检查导出功能可用性"""
    try:
        dependencies = export_service.check_dependencies()
        return jsonify({
            'code': 200,
            'data': {
                'excel': dependencies['excel'],
                'pdf': dependencies['pdf']
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

