"""
Database models for ORC Web Application
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User account model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    api_configs = db.relationship('APIConfig', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    projects = db.relationship('Project', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    analyses = db.relationship('AnalysisHistory', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class APIConfig(db.Model):
    """User's API provider configurations"""
    __tablename__ = 'api_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    provider = db.Column(db.String(50), nullable=False)  # ollama, groq, openai, etc.
    api_key = db.Column(db.String(255))  # Encrypted/masked
    model_name = db.Column(db.String(100))
    base_url = db.Column(db.String(255))  # For Ollama local installs
    is_active = db.Column(db.Boolean, default=True)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<APIConfig {self.provider} for user {self.user_id}>'


class Project(db.Model):
    """User's indexed codebase projects"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    path = db.Column(db.String(500))
    description = db.Column(db.Text)
    db_path = db.Column(db.String(500))  # Path to .orc/index.db
    last_indexed = db.Column(db.DateTime)
    file_count = db.Column(db.Integer, default=0)
    function_count = db.Column(db.Integer, default=0)
    class_count = db.Column(db.Integer, default=0)
    lines_of_code = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    analyses = db.relationship('AnalysisHistory', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Project {self.name}>'


class AnalysisHistory(db.Model):
    """History of code analyses performed"""
    __tablename__ = 'analysis_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    analysis_type = db.Column(db.String(50), nullable=False)  # dead_code, complexity, security, etc.
    results = db.Column(db.JSON)  # Store results as JSON
    summary = db.Column(db.Text)  # Human-readable summary
    status = db.Column(db.String(20), default='completed')  # pending, completed, failed
    error_message = db.Column(db.Text)
    execution_time = db.Column(db.Float)  # Time in seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AnalysisHistory {self.analysis_type} on project {self.project_id}>'
