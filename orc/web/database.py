"""
Database initialization and configuration
"""
from orc.web.models import db, User, APIConfig, Project, AnalysisHistory


def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print('Database tables created successfully')


def reset_db(app):
    """Reset database (drop all tables and recreate)"""
    with app.app_context():
        db.drop_all()
        db.create_all()
        print('Database reset successfully')


def create_sample_user(app, username='admin', email='admin@orc.dev', password='admin123'):
    """Create a sample user for testing"""
    with app.app_context():
        # Check if user exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f'User {username} already exists')
            return existing_user
        
        # Create new user
        user = User(
            username=username,
            email=email,
            full_name='ORC Administrator'
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        print(f'Sample user created: {username} / {password}')
        return user
