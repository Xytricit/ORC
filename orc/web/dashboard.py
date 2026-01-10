"""
Dashboard routes
"""
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from orc.web.models import db, Project, AnalysisHistory, APIConfig
from datetime import datetime, timedelta

dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard.route('/api-docs')
@login_required
def api_docs():
    """API documentation page"""
    return render_template('api_docs.html')


@dashboard.route('/')
@login_required
def home():
    """Dashboard home page"""
    # Get user stats
    project_count = Project.query.filter_by(user_id=current_user.id).count()
    analysis_count = AnalysisHistory.query.filter_by(user_id=current_user.id).count()
    api_configs_count = APIConfig.query.filter_by(user_id=current_user.id).count()
    
    # Recent analyses count (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_analysis_count = AnalysisHistory.query.filter(
        AnalysisHistory.user_id == current_user.id,
        AnalysisHistory.created_at >= week_ago
    ).count()
    
    # Get recent activities
    recent_analyses = AnalysisHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(AnalysisHistory.created_at.desc()).limit(5).all()
    
    recent_activities = []
    for analysis in recent_analyses:
        # Calculate time ago
        time_diff = datetime.utcnow() - analysis.created_at
        if time_diff.days > 0:
            time_ago = f"{time_diff.days}d ago"
        elif time_diff.seconds // 3600 > 0:
            time_ago = f"{time_diff.seconds // 3600}h ago"
        else:
            time_ago = f"{time_diff.seconds // 60}m ago"
        
        recent_activities.append({
            'type': analysis.analysis_type,
            'title': f"{analysis.analysis_type.replace('_', ' ').title()} Analysis",
            'description': analysis.summary or f"Completed {analysis.analysis_type} analysis",
            'time': time_ago
        })
    
    # Calculate dead code found (example - would come from actual analyses)
    dead_code_found = 0
    try:
        dead_code_analyses = AnalysisHistory.query.filter_by(
            user_id=current_user.id,
            analysis_type='dead_code'
        ).all()
        for analysis in dead_code_analyses:
            if analysis.results and isinstance(analysis.results, dict):
                safe_list = analysis.results.get('safe_to_delete', [])
                if safe_list and isinstance(safe_list, list):
                    dead_code_found += len(safe_list)
    except Exception:
        dead_code_found = 0
    
    # Safely convert counts to integers
    def safe_int(value, default=0):
        """Safely convert value to int, handling None and other types"""
        try:
            if value is None:
                return default
            return int(value)
        except (ValueError, TypeError):
            return default
    
    return render_template(
        'dashboard/home.html',
        project_count=safe_int(project_count),
        analysis_count=safe_int(analysis_count),
        recent_analysis_count=safe_int(recent_analysis_count),
        api_configs_count=safe_int(api_configs_count),
        dead_code_found=safe_int(dead_code_found),
        recent_activities=recent_activities or []
    )
