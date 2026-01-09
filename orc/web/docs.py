"""
ORC Documentation Routes
"""
from flask import Blueprint, render_template
from flask_login import login_required

docs = Blueprint('docs', __name__, url_prefix='/docs')


@docs.route('/')
def index():
    """Documentation home page"""
    return render_template('docs/index.html')


@docs.route('/getting-started')
def getting_started():
    """Getting started guide"""
    return render_template('docs/getting_started.html')


@docs.route('/cli')
def cli_docs():
    """CLI documentation"""
    return render_template('docs/cli.html')


@docs.route('/web')
def web_docs():
    """Web interface documentation"""
    return render_template('docs/web.html')


@docs.route('/api')
def api_docs():
    """API documentation"""
    return render_template('docs/api.html')


@docs.route('/tutorials')
def tutorials():
    """Tutorials page"""
    return render_template('docs/tutorials.html')


@docs.route('/tutorials/first-analysis')
def tutorial_first_analysis():
    """Tutorial: Your first analysis"""
    return render_template('docs/tutorial_first_analysis.html')


@docs.route('/tutorials/ai-chat')
def tutorial_ai_chat():
    """Tutorial: Using AI chat"""
    return render_template('docs/tutorial_ai_chat.html')


@docs.route('/tutorials/web-setup')
def tutorial_web_setup():
    """Tutorial: Setting up the web interface"""
    return render_template('docs/tutorial_web_setup.html')
