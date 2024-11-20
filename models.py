from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class MediaRequest(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(20), nullable=False)
    detailed_description = db.Column(db.Text, nullable=True)
    submitted_by = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='Open')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<MediaRequest {self.title}>'

