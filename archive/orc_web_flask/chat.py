"""
AI Chat routes - Context-aware AI assistant
"""
from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from orc.web.models import db, Project, APIConfig
import os

chat = Blueprint('chat', __name__, url_prefix='/chat')


@chat.route('/')
@login_required
def index():
    """AI chat interface"""
    projects = Project.query.filter_by(user_id=current_user.id).all()
    
    # Get configured AI providers
    configs = APIConfig.query.filter_by(user_id=current_user.id, is_active=True).all()
    
    # Get default provider
    default_config = next((c for c in configs if c.is_default), configs[0] if configs else None)
    
    return render_template('chat/index.html', 
                         projects=projects,
                         configs=configs,
                         default_config=default_config)


@chat.route('/send', methods=['POST'])
@login_required
def send_message():
    """Send message to AI and get response"""
    data = request.json
    message = data.get('message')
    project_id = data.get('project_id')
    provider_id = data.get('provider_id')
    
    if not message:
        return jsonify({'error': 'Message required'}), 400
    
    try:
        # Get project if specified
        project = None
        context = None
        if project_id:
            project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
            if project and project.last_indexed:
                # Get context from ORC index
                from orc.ai_tools import ORCTools
                tools = ORCTools(db_path=project.db_path)
                stats = tools.get_codebase_stats()
                
                context = f"""You are analyzing the project: {project.name}
Project stats: {stats.get('total_files', 0)} files, {stats.get('total_functions', 0)} functions, {stats.get('total_classes', 0)} classes.
Use this context to provide accurate, project-specific answers."""
        
        # Get AI provider config
        if provider_id:
            config = APIConfig.query.filter_by(id=provider_id, user_id=current_user.id).first()
        else:
            config = APIConfig.query.filter_by(user_id=current_user.id, is_default=True).first()
        
        if not config:
            return jsonify({'error': 'No AI provider configured. Please configure one in Settings > API Config.'}), 400
        
        # Call AI based on provider
        response = call_ai_provider(config, message, context)
        
        return jsonify({
            'response': response,
            'provider': config.provider,
            'project': project.name if project else None
        })
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


def call_ai_provider(config, message, context=None):
    """Call the configured AI provider"""
    provider = config.provider
    
    # Build full prompt
    full_message = message
    if context:
        full_message = f"{context}\n\nUser question: {message}"
    
    try:
        if provider == 'ollama':
            import httpx
            response = httpx.post(
                f"{config.base_url or 'http://localhost:11434'}/api/generate",
                json={
                    'model': config.model_name or 'llama3.1',
                    'prompt': full_message,
                    'stream': False
                },
                timeout=60.0
            )
            return response.json().get('response', 'No response')
            
        elif provider == 'groq':
            from groq import Groq
            client = Groq(api_key=config.api_key)
            completion = client.chat.completions.create(
                model=config.model_name or "llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": full_message}],
                max_tokens=2000
            )
            return completion.choices[0].message.content
            
        elif provider == 'openai':
            from openai import OpenAI
            client = OpenAI(api_key=config.api_key)
            completion = client.chat.completions.create(
                model=config.model_name or "gpt-4o-mini",
                messages=[{"role": "user", "content": full_message}],
                max_tokens=2000
            )
            return completion.choices[0].message.content
            
        elif provider == 'anthropic':
            from anthropic import Anthropic
            client = Anthropic(api_key=config.api_key)
            message = client.messages.create(
                model=config.model_name or "claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": full_message}]
            )
            return message.content[0].text
            
        elif provider == 'gemini':
            import google.generativeai as genai
            genai.configure(api_key=config.api_key)
            model = genai.GenerativeModel(config.model_name or 'gemini-1.5-flash')
            response = model.generate_content(full_message)
            return response.text
            
        else:
            return f"Provider {provider} not yet implemented. Please use Ollama, Groq, OpenAI, Anthropic, or Gemini."
            
    except Exception as e:
        return f"Error calling {provider}: {str(e)}"
