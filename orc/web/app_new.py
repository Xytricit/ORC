"""
ORC Web Application - Main Entry Point
"""
from flask import Flask, render_template
from flask_login import LoginManager
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orc.web.models import db, User
from orc.web.auth import auth
from orc.web.dashboard import dashboard
from orc.web.projects import projects
from orc.web.settings import settings, analysis
from orc.web.chat import chat
from orc.web.api import api_bp, api
from orc.web.docs import docs
from orc.web.database import init_db

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('ORC_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orc_web.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = True

# Initialize extensions
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.signin'
login_manager.login_message = 'Please sign in to access this page.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))


# Context processor to inject project_count into sidebar
@app.context_processor
def inject_globals():
    from flask_login import current_user
    if current_user.is_authenticated:
        from orc.web.models import Project
        project_count = Project.query.filter_by(user_id=current_user.id).count()
        return dict(project_count=project_count)
    return dict(project_count=0)


# Register blueprints
from flask import Blueprint
main = Blueprint('main', __name__)

@main.route('/')
def landing():
    """Landing page"""
    return render_template('landing.html')

app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(dashboard)
app.register_blueprint(projects)
app.register_blueprint(settings)
app.register_blueprint(analysis)
app.register_blueprint(chat)
app.register_blueprint(api_bp)
app.register_blueprint(api)
app.register_blueprint(docs)


# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors with custom page"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return render_template('error.html', error='Internal server error occurred'), 500


# Initialize database
with app.app_context():
    db.create_all()
    print('Database initialized')


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
