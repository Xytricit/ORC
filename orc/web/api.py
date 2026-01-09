"""
ORC Context API - For external AI IDEs and CLI
This API allows AI coding assistants and CLI to query ORC's index
to get smart context recommendations and save tokens.
"""
from flask import Blueprint, request, jsonify
from functools import wraps
from orc.web.models import db, Project, User, APIConfig
from orc.web.models_tokens import CLIToken
from datetime import datetime
import os

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')
api = Blueprint('api_cli', __name__, url_prefix='/api')  # CLI API endpoints


def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({'error': 'API key required', 'message': 'Include X-API-Key header'}), 401
        
        # Find user by checking if API key matches username:api_key format
        # In production, use proper API key table
        # For now, accept any key in format "username:password"
        try:
            username = api_key.split(':')[0] if ':' in api_key else api_key
            user = User.query.filter_by(username=username).first()
            if not user:
                return jsonify({'error': 'Invalid API key'}), 401
            request.current_user = user
        except:
            return jsonify({'error': 'Invalid API key format'}), 401
        
        return f(*args, **kwargs)
    return decorated_function


@api_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'service': 'ORC Context API'
    })


@api_bp.route('/projects', methods=['GET'])
@require_api_key
def list_projects():
    """List all indexed projects for the authenticated user"""
    projects = Project.query.filter_by(user_id=request.current_user.id).all()
    
    return jsonify({
        'projects': [{
            'id': p.id,
            'name': p.name,
            'path': p.path,
            'indexed': p.last_indexed is not None,
            'files': p.file_count,
            'functions': p.function_count,
            'classes': p.class_count
        } for p in projects]
    })


@api_bp.route('/context/query', methods=['POST'])
@require_api_key
def query_context():
    """
    Smart context query - Get relevant files based on user query
    
    Request body:
    {
        "project_id": 1,
        "query": "authentication logic",
        "max_files": 5
    }
    
    Response:
    {
        "relevant_files": [
            {
                "path": "src/auth.py",
                "reason": "Contains authentication functions",
                "functions": ["login", "logout", "verify_token"],
                "relevance_score": 0.95
            }
        ]
    }
    """
    data = request.json
    project_id = data.get('project_id')
    query = data.get('query', '')
    max_files = data.get('max_files', 5)
    
    if not project_id:
        return jsonify({'error': 'project_id required'}), 400
    
    project = Project.query.filter_by(id=project_id, user_id=request.current_user.id).first()
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if not project.last_indexed:
        return jsonify({'error': 'Project not indexed'}), 400
    
    try:
        from orc.ai_tools import ORCTools
        tools = ORCTools(db_path=project.db_path)
        
        # Search functions matching query
        functions_result = tools.query_functions(pattern=query, limit=max_files * 3)
        functions = functions_result.get('functions', [])
        
        # Group by file and rank
        file_relevance = {}
        for func in functions:
            file_path = func.get('file_path', '')
            if file_path not in file_relevance:
                file_relevance[file_path] = {
                    'path': file_path,
                    'functions': [],
                    'relevance_score': 0,
                    'reason': []
                }
            file_relevance[file_path]['functions'].append(func.get('name'))
            file_relevance[file_path]['relevance_score'] += 1
        
        # Sort by relevance and limit
        sorted_files = sorted(
            file_relevance.values(), 
            key=lambda x: x['relevance_score'], 
            reverse=True
        )[:max_files]
        
        # Add reasons
        for file_info in sorted_files:
            func_count = len(file_info['functions'])
            file_info['reason'] = f"Contains {func_count} function(s) matching '{query}'"
            file_info['relevance_score'] = min(file_info['relevance_score'] / 10, 1.0)
        
        return jsonify({
            'project': project.name,
            'query': query,
            'relevant_files': sorted_files,
            'total_matches': len(functions),
            'message': f'Found {len(sorted_files)} relevant files for your query'
        })
        
    except Exception as e:
        return jsonify({'error': f'Query failed: {str(e)}'}), 500


@api_bp.route('/context/smart-files', methods=['POST'])
@require_api_key
def get_smart_files():
    """
    Get smart file recommendations based on task description
    
    Request:
    {
        "project_id": 1,
        "task": "Fix the login bug where users can't reset password",
        "context_window": 8000  # token limit
    }
    
    Response:
    {
        "recommended_files": ["auth.py", "user.py", "reset.py"],
        "estimated_tokens": 3500,
        "reasoning": "These files contain authentication and password reset logic"
    }
    """
    data = request.json
    project_id = data.get('project_id')
    task = data.get('task', '')
    context_window = data.get('context_window', 8000)
    
    if not project_id or not task:
        return jsonify({'error': 'project_id and task required'}), 400
    
    project = Project.query.filter_by(id=project_id, user_id=request.current_user.id).first()
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    try:
        from orc.ai_tools import ORCTools
        tools = ORCTools(db_path=project.db_path)
        
        # Extract keywords from task
        keywords = extract_keywords(task)
        
        # Search for relevant files
        relevant_files = []
        estimated_tokens = 0
        
        for keyword in keywords[:3]:  # Top 3 keywords
            result = tools.query_functions(pattern=keyword, limit=10)
            for func in result.get('functions', []):
                file_path = func.get('file_path')
                if file_path and file_path not in relevant_files:
                    # Estimate tokens (rough: 4 chars = 1 token)
                    func_lines = func.get('end_line', 0) - func.get('start_line', 0)
                    estimated_tokens += func_lines * 20  # ~20 tokens per line
                    
                    if estimated_tokens < context_window * 0.8:  # Leave 20% buffer
                        relevant_files.append(file_path)
        
        return jsonify({
            'project': project.name,
            'task': task,
            'recommended_files': relevant_files[:10],
            'estimated_tokens': estimated_tokens,
            'context_window': context_window,
            'reasoning': f'Files containing: {", ".join(keywords[:3])}',
            'keywords_detected': keywords
        })
        
    except Exception as e:
        return jsonify({'error': f'Smart file selection failed: {str(e)}'}), 500


@api_bp.route('/context/dependencies', methods=['POST'])
@require_api_key
def get_dependencies():
    """
    Get file dependencies - what files are related to this one
    
    Request:
    {
        "project_id": 1,
        "file_path": "src/auth.py"
    }
    
    Response:
    {
        "dependencies": ["src/user.py", "src/db.py"],
        "dependents": ["src/api.py", "src/routes.py"]
    }
    """
    data = request.json
    project_id = data.get('project_id')
    file_path = data.get('file_path', '')
    
    if not project_id or not file_path:
        return jsonify({'error': 'project_id and file_path required'}), 400
    
    project = Project.query.filter_by(id=project_id, user_id=request.current_user.id).first()
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    try:
        # This would use the dependency graph from ORC
        # For now, return placeholder
        return jsonify({
            'file': file_path,
            'dependencies': [],
            'dependents': [],
            'message': 'Dependency analysis available in future version'
        })
        
    except Exception as e:
        return jsonify({'error': f'Dependency analysis failed: {str(e)}'}), 500


def extract_keywords(text):
    """Extract important keywords from text"""
    # Simple keyword extraction
    # In production, use NLP
    import re
    words = re.findall(r'\w+', text.lower())
    
    # Common words to ignore
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                 'fix', 'bug', 'where', 'can', 'cant', 'issue', 'problem'}
    
    keywords = [w for w in words if w not in stopwords and len(w) > 3]
    
    # Return unique keywords
    return list(dict.fromkeys(keywords))


# ============================================================================
# CLI Integration Endpoints
# ============================================================================

def require_cli_token(f):
    """Decorator to require CLI token authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('X-CLI-Token')
        
        if not token:
            return jsonify({'error': 'CLI token required'}), 401
        
        cli_token = CLIToken.query.filter_by(token=token, is_active=True).first()
        
        if not cli_token:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Update last used
        cli_token.last_used = datetime.utcnow()
        db.session.commit()
        
        # Pass user to the function
        return f(cli_token.user, *args, **kwargs)
    
    return decorated_function


@api.route('/token/generate', methods=['POST'])
def generate_token():
    """Generate a new CLI token for authenticated web user"""
    from flask_login import current_user
    
    if not current_user.is_authenticated:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Generate token
    token_value = CLIToken.generate_token()
    
    # Create token record
    cli_token = CLIToken(
        user_id=current_user.id,
        token=token_value,
        name=f'CLI Token {datetime.utcnow().strftime("%Y-%m-%d")}'
    )
    
    try:
        db.session.add(cli_token)
        db.session.commit()
        
        return jsonify({
            'token': token_value,
            'created_at': cli_token.created_at.isoformat()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api.route('/configs', methods=['GET'])
@require_cli_token
def get_configs(user):
    """Get user's API configurations for CLI"""
    configs = APIConfig.query.filter_by(user_id=user.id, is_active=True).all()
    
    result = []
    for config in configs:
        result.append({
            'provider': config.provider,
            'api_key': config.api_key,
            'model_name': config.model_name,
            'base_url': config.base_url,
            'is_default': config.is_default
        })
    
    return jsonify({
        'configs': result,
        'user': {
            'username': user.username,
            'email': user.email
        }
    })


@api.route('/config/<provider>', methods=['GET'])
@require_cli_token
def get_provider_config(user, provider):
    """Get specific provider configuration"""
    config = APIConfig.query.filter_by(
        user_id=user.id,
        provider=provider,
        is_active=True
    ).first()
    
    if not config:
        return jsonify({'error': f'No configuration for {provider}'}), 404
    
    return jsonify({
        'provider': config.provider,
        'api_key': config.api_key,
        'model_name': config.model_name,
        'base_url': config.base_url,
        'is_default': config.is_default
    })


@api.route('/default-config', methods=['GET'])
@require_cli_token
def get_default_config(user):
    """Get user's default AI provider configuration"""
    config = APIConfig.query.filter_by(
        user_id=user.id,
        is_default=True,
        is_active=True
    ).first()
    
    if not config:
        # Get any active config
        config = APIConfig.query.filter_by(
            user_id=user.id,
            is_active=True
        ).first()
    
    if not config:
        return jsonify({'error': 'No AI provider configured'}), 404
    
    return jsonify({
        'provider': config.provider,
        'api_key': config.api_key,
        'model_name': config.model_name,
        'base_url': config.base_url
    })


@api.route('/projects/auto-create', methods=['POST'])
@require_cli_token
def auto_create_project(user):
    """Auto-create a project from CLI"""
    data = request.json
    
    project_name = data.get('name')
    project_path = data.get('path')
    db_path = data.get('db_path')
    
    if not project_name or not project_path:
        return jsonify({'error': 'name and path required'}), 400
    
    # Check if project already exists
    existing = Project.query.filter_by(
        user_id=user.id,
        path=project_path
    ).first()
    
    if existing:
        return jsonify({'message': 'Project already exists', 'project_id': existing.id}), 200
    
    # Create new project
    project = Project(
        user_id=user.id,
        name=project_name,
        path=project_path,
        db_path=db_path,
        description=f'Auto-created from CLI in {project_path}'
    )
    
    try:
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            'message': 'Project created',
            'project_id': project.id,
            'name': project.name
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
