"""查询记录模型"""
from datetime import datetime
from app import db


class QueryLog(db.Model):
    """查询记录表"""
    __tablename__ = 'query_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False, index=True)
    tv_show = db.Column(db.String(200))
    season_episode = db.Column(db.String(50))
    context_note = db.Column(db.Text)
    query_time = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'word_id': self.word_id,
            'tv_show': self.tv_show,
            'season_episode': self.season_episode,
            'context_note': self.context_note,
            'query_time': self.query_time.isoformat() if self.query_time else None
        }

