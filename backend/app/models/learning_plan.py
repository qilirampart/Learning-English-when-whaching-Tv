"""学习计划模型"""
from datetime import datetime, timedelta
from app import db


class LearningPlan(db.Model):
    """学习计划表"""
    __tablename__ = 'learning_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), unique=True, nullable=False, index=True)
    mastery_level = db.Column(db.Integer, default=0)  # 0-5级
    review_count = db.Column(db.Integer, default=0)
    last_review = db.Column(db.DateTime)
    next_review = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    is_mastered = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 艾宾浩斯遗忘曲线间隔（天）
    REVIEW_INTERVALS = [1, 2, 4, 7, 15]
    
    def calculate_next_review(self, is_correct):
        """
        计算下次复习时间
        :param is_correct: 本次复习是否正确
        """
        if is_correct:
            # 答对了，提升掌握度
            self.mastery_level = min(self.mastery_level + 1, 5)
            if self.mastery_level >= len(self.REVIEW_INTERVALS):
                # 已完全掌握
                self.is_mastered = True
                self.next_review = None
            else:
                # 计算下次复习时间
                interval = self.REVIEW_INTERVALS[self.mastery_level]
                self.next_review = datetime.utcnow() + timedelta(days=interval)
        else:
            # 答错了，重置掌握度
            self.mastery_level = max(self.mastery_level - 1, 0)
            self.is_mastered = False
            interval = self.REVIEW_INTERVALS[0]
            self.next_review = datetime.utcnow() + timedelta(days=interval)
        
        self.review_count += 1
        self.last_review = datetime.utcnow()
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'word_id': self.word_id,
            'mastery_level': self.mastery_level,
            'review_count': self.review_count,
            'last_review': self.last_review.isoformat() if self.last_review else None,
            'next_review': self.next_review.isoformat() if self.next_review else None,
            'is_mastered': self.is_mastered,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

