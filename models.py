from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
class MatrixDevice(db.Model):
    __tablename__ = 'matrix_devices'
    
    id = db.Column(db.String(10), primary_key=True)  # Device ID like "47ab"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(50))
    wifi_ssid = db.Column(db.String(50))
    wifi_password = db.Column(db.String(50))
    last_seen = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='matrix_devices')
    configs = db.relationship('MatrixAppConfig', backref='device', lazy=True)

class MatrixAppConfig(db.Model):
    __tablename__ = 'matrix_app_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(10), db.ForeignKey('matrix_devices.id'))
    app_type = db.Column(db.String(20))  # 'clock', 'weather', 'stocks', etc.
    settings = db.Column(db.JSON)
    display_order = db.Column(db.Integer)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
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
    torrent_link = db.Column(db.String(255), nullable=True)  # Stores the torrent link
    save_path = db.Column(db.String(255), nullable=True)     # Stores the download location
    progress = db.Column(db.Float, default=0.0)              # Stores the download progress
    torrent_hash = db.Column(db.String(40), nullable=True)   # Stores the torrent hash for better identification

    def __repr__(self):
        return f'<MediaRequest {self.title}>'

