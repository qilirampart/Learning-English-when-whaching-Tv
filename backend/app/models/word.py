"""单词模型"""
from datetime import datetime
from app import db


class Word(db.Model):
    """单词表"""
    __tablename__ = 'words'
    
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), unique=True, nullable=False, index=True)
    phonetic = db.Column(db.String(100))
    translation = db.Column(db.Text)
    definition = db.Column(db.Text)
    examples = db.Column(db.Text)  # JSON格式存储例句
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联关系
    query_logs = db.relationship('QueryLog', backref='word', lazy='dynamic')
    learning_plan = db.relationship('LearningPlan', backref='word', uselist=False)
    review_logs = db.relationship('ReviewLog', backref='word', lazy='dynamic')
    
    def to_dict(self):
        """转换为字典"""
        import json
        return {
            'id': self.id,
            'word': self.word,
            'phonetic': self.phonetic,
            'translation': self.translation,
            'definition': self.definition,
            'examples': json.loads(self.examples) if self.examples else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'query_count': self.query_logs.count()
        }

