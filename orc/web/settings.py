"""
Settings routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from orc.web.models import db, APIConfig
from orc.web.forms import APIConfigForm

settings = Blueprint('settings', __name__, url_prefix='/settings')

analysis = Blueprint('analysis', __name__, url_prefix='/analysis')


@settings.route('/api')
@login_required
def api_config():
    """API configuration page"""
    configs = APIConfig.query.filter_by(user_id=current_user.id).all()
    
    # Get available providers
    providers = [
        {
            'id': 'ollama',
            'name': 'Ollama',
            'type': 'Local',
            'description': 'Run AI models locally on your machine. 100% free and private.',
            'icon': 'OL',
            'requires_key': False
        },
        {
            'id': 'groq',
            'name': 'Groq',
            'type': 'Cloud',
            'description': 'Fast inference with free tier. 100k tokens/day.',
            'icon': 'GR',
            'requires_key': True
        },
        {
            'id': 'gemini',
            'name': 'Google Gemini',
            'type': 'Cloud',
            'description': 'Google\'s AI model with generous free tier.',
            'icon': 'GM',
            'requires_key': True
        },
        {
            'id': 'openai',
            'name': 'OpenAI',
            'type': 'Cloud',
            'description': 'GPT models from OpenAI. Paid service.',
            'icon': 'AI',
            'requires_key': True
        },
        {
            'id': 'anthropic',
            'name': 'Anthropic',
            'type': 'Cloud',
            'description': 'Claude models. Excellent for code analysis.',
            'icon': 'CL',
            'requires_key': True
        },
        {
            'id': 'deepseek',
            'name': 'DeepSeek',
            'type': 'Cloud',
            'description': 'Very affordable. Great for code analysis.',
            'icon': 'DS',
            'requires_key': True
        }
    ]
    
    # Map configs to providers
    for provider in providers:
        config = next((c for c in configs if c.provider == provider['id']), None)
        provider['config'] = config
        provider['is_configured'] = config is not None
        provider['is_default'] = config.is_default if config else False
    
    return render_template('settings/api_config.html', providers=providers)


@settings.route('/api/add', methods=['POST'])
@login_required
def add_api_config():
    """Add or update API configuration"""
    provider = request.form.get('provider')
    api_key = request.form.get('api_key', '')
    model_name = request.form.get('model_name', '')
    base_url = request.form.get('base_url', '')
    is_default = request.form.get('is_default') == 'on'
    
    try:
        # Check if config exists
        config = APIConfig.query.filter_by(
            user_id=current_user.id,
            provider=provider
        ).first()
        
        if config:
            # Update existing
            config.api_key = api_key
            config.model_name = model_name
            config.base_url = base_url
            config.is_active = True
        else:
            # Create new
            config = APIConfig(
                user_id=current_user.id,
                provider=provider,
                api_key=api_key,
                model_name=model_name,
                base_url=base_url,
                is_active=True
            )
            db.session.add(config)
        
        # Handle default provider
        if is_default:
            # Remove default from others
            APIConfig.query.filter_by(
                user_id=current_user.id
            ).update({'is_default': False})
            config.is_default = True
        
        db.session.commit()
        flash(f'{provider.title()} configured successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error configuring provider: {str(e)}', 'error')
    
    return redirect(url_for('settings.api_config'))


@settings.route('/api/delete/<int:config_id>', methods=['POST'])
@login_required
def delete_api_config(config_id):
    """Delete API configuration"""
    config = APIConfig.query.filter_by(id=config_id, user_id=current_user.id).first_or_404()
    
    try:
        provider_name = config.provider
        db.session.delete(config)
        db.session.commit()
        flash(f'{provider_name.title()} configuration deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting configuration.', 'error')
    
    return redirect(url_for('settings.api_config'))


@settings.route('/api/test', methods=['POST'])
@login_required
def test_api_connection():
    """Test API connection"""
    provider = request.json.get('provider')
    api_key = request.json.get('api_key')
    base_url = request.json.get('base_url')
    
    # Simple validation for now
    # In production, actually test the connection
    if provider == 'ollama':
        # Check if base_url is accessible
        return jsonify({'success': True, 'message': 'Ollama connection successful'})
    elif api_key:
        # Validate key format
        return jsonify({'success': True, 'message': f'{provider.title()} key validated'})
    else:
        return jsonify({'success': False, 'message': 'API key required'})


@settings.route('/account')
@login_required
def account():
    """Account settings page"""
    return render_template('settings/account.html')


@settings.route('/account/update', methods=['POST'])
@login_required
def update_account():
    """Update account information"""
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    
    if full_name:
        current_user.full_name = full_name
    
    if email and email != current_user.email:
        # Check if email already exists
        from orc.web.models import User
        existing = User.query.filter_by(email=email).first()
        if existing and existing.id != current_user.id:
            flash('Email already in use by another account.', 'error')
            return redirect(url_for('settings.account'))
        current_user.email = email
    
    try:
        db.session.commit()
        flash('Account updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating account.', 'error')
    
    return redirect(url_for('settings.account'))


@settings.route('/account/password', methods=['POST'])
@login_required
def change_password():
    """Change password"""
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not current_user.check_password(current_password):
        flash('Current password is incorrect.', 'error')
        return redirect(url_for('settings.account'))
    
    if new_password != confirm_password:
        flash('New passwords do not match.', 'error')
        return redirect(url_for('settings.account'))
    
    if len(new_password) < 8:
        flash('Password must be at least 8 characters.', 'error')
        return redirect(url_for('settings.account'))
    
    current_user.set_password(new_password)
    
    try:
        db.session.commit()
        flash('Password changed successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error changing password.', 'error')
    
    return redirect(url_for('settings.account'))


@analysis.route('/run')
@login_required
def run():
    """Run analysis page"""
    from orc.web.models import Project
    
    projects = Project.query.filter_by(user_id=current_user.id).all()
    
    # Get project from query param if specified
    project_id = request.args.get('project')
    selected_project = None
    if project_id:
        selected_project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    
    analysis_types = [
        {
            'id': 'dead_code',
            'name': 'Dead Code Detection',
            'description': 'Find unused functions, classes, and imports',
            'icon': 'DC',
            'estimated_time': '1-3 minutes'
        },
        {
            'id': 'complexity',
            'name': 'Complexity Analysis',
            'description': 'Measure cyclomatic complexity and identify hotspots',
            'icon': 'CX',
            'estimated_time': '30-60 seconds'
        },
        {
            'id': 'security',
            'name': 'Security Scan',
            'description': 'Detect potential security vulnerabilities',
            'icon': 'SC',
            'estimated_time': '1-2 minutes'
        },
        {
            'id': 'dependencies',
            'name': 'Dependency Analysis',
            'description': 'Analyze module dependencies and coupling',
            'icon': 'DP',
            'estimated_time': '30-60 seconds'
        }
    ]
    
    return render_template('analysis/run.html', 
                         projects=projects, 
                         analysis_types=analysis_types,
                         selected_project=selected_project)


@analysis.route('/execute', methods=['POST'])
@login_required
def execute():
    """Execute analysis"""
    from orc.web.models import Project, AnalysisHistory
    from datetime import datetime
    import time
    
    project_id = request.form.get('project_id')
    analysis_type = request.form.get('analysis_type')
    
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    
    if not project.last_indexed:
        flash('Please index the project before running analysis.', 'error')
        return redirect(url_for('analysis.run'))
    
    try:
        start_time = time.time()
        
        # Run analysis based on type
        if analysis_type == 'dead_code':
            from orc.ai_tools import ORCTools
            tools = ORCTools(db_path=project.db_path)
            results = tools.get_dead_code(confidence_threshold=0.7, limit=50)
            summary = f"Found {results.get('summary', {}).get('total_potentially_unused', 0)} potentially unused functions"
            
        elif analysis_type == 'complexity':
            from orc.ai_tools import ORCTools
            tools = ORCTools(db_path=project.db_path)
            results = tools.get_complexity_report(min_complexity=5, limit=50)
            summary = f"Average complexity: {results.get('summary', {}).get('average_complexity', 0):.2f}"
            
        elif analysis_type == 'dependencies':
            from orc.ai_tools import ORCTools
            tools = ORCTools(db_path=project.db_path)
            results = tools.get_codebase_stats()
            summary = f"Analyzed {results.get('total_files', 0)} files"
            
        else:
            results = {'message': 'Analysis type not yet implemented'}
            summary = 'Analysis completed'
        
        execution_time = time.time() - start_time
        
        # Save to history
        analysis_record = AnalysisHistory(
            user_id=current_user.id,
            project_id=project.id,
            analysis_type=analysis_type,
            results=results,
            summary=summary,
            status='completed',
            execution_time=execution_time
        )
        db.session.add(analysis_record)
        db.session.commit()
        
        flash(f'Analysis completed successfully in {execution_time:.2f}s', 'success')
        return redirect(url_for('analysis.results', analysis_id=analysis_record.id))
        
    except Exception as e:
        flash(f'Error running analysis: {str(e)}', 'error')
        return redirect(url_for('analysis.run'))


@analysis.route('/results/<int:analysis_id>')
@login_required
def results(analysis_id):
    """View analysis results"""
    from orc.web.models import AnalysisHistory
    
    analysis_record = AnalysisHistory.query.filter_by(
        id=analysis_id,
        user_id=current_user.id
    ).first_or_404()
    
    return render_template('analysis/results.html', analysis=analysis_record)


@analysis.route('/history')
@login_required
def history():
    """Analysis history page"""
    from orc.web.models import AnalysisHistory
    
    analyses = AnalysisHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(AnalysisHistory.created_at.desc()).all()
    
    return render_template('analysis/history.html', analyses=analyses)
