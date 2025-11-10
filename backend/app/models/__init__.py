"""数据库模型"""
from app.models.word import Word
from app.models.query_log import QueryLog
from app.models.learning_plan import LearningPlan
from app.models.review_log import ReviewLog

__all__ = ['Word', 'QueryLog', 'LearningPlan', 'ReviewLog']

