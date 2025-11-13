"""复习记录模型"""
from datetime import datetime
from app import db


class ReviewLog(db.Model):
    """复习记录表"""
    __tablename__ = 'review_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False, index=True)
    is_correct = db.Column(db.Boolean)
    review_time = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    time_spent = db.Column(db.Integer)  # 用时（秒）
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'word_id': self.word_id,
            'is_correct': self.is_correct,
            'review_time': self.review_time.isoformat() if self.review_time else None,
            'time_spent': self.time_spent
        }

