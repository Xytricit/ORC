"""
CLI Authentication Token Model
"""
from orc.web.models import db
from datetime import datetime
import secrets


class CLIToken(db.Model):
    """CLI authentication tokens for API access"""
    __tablename__ = 'cli_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), default='CLI Token')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('cli_tokens', lazy='dynamic'))
    
    @staticmethod
    def generate_token():
        """Generate a secure random token"""
        return secrets.token_urlsafe(48)
    
    def __repr__(self):
        return f'<CLIToken {self.name} for user {self.user_id}>'
