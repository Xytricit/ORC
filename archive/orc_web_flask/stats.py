"""
Stats routes for codebase statistics
"""
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from orc.web.models import db, Project, AnalysisHistory
from sqlalchemy import func
from datetime import datetime, timedelta

stats = Blueprint('stats', __name__, url_prefix='/stats')


@stats.route('/')
@login_required
def overview():
    """Stats overview page showing all projects and their metrics"""
    # Get all user projects with their stats
    projects = Project.query.filter_by(user_id=current_user.id).all()
    
    project_stats = []
    total_files = 0
    total_functions = 0
    total_lines = 0
    total_classes = 0
    
    for project in projects:
        # Get analysis count for this project
        analysis_count = AnalysisHistory.query.filter_by(
            user_id=current_user.id,
            project_id=project.id
        ).count()
        
        # Get latest analysis
        latest_analysis = AnalysisHistory.query.filter_by(
            user_id=current_user.id,
            project_id=project.id
        ).order_by(AnalysisHistory.created_at.desc()).first()
        
        # Calculate days since last index
        days_since_index = None
        if project.last_indexed:
            days_since_index = (datetime.utcnow() - project.last_indexed).days
        
        project_stats.append({
            'id': project.id,
            'name': project.name,
            'path': project.path,
            'file_count': project.file_count or 0,
            'function_count': project.function_count or 0,
            'class_count': project.class_count or 0,
            'lines_of_code': project.lines_of_code or 0,
            'analysis_count': analysis_count,
            'last_indexed': project.last_indexed,
            'days_since_index': days_since_index,
            'latest_analysis_type': latest_analysis.analysis_type if latest_analysis else None,
            'created_at': project.created_at
        })
        
        # Add to totals
        total_files += project.file_count or 0
        total_functions += project.function_count or 0
        total_lines += project.lines_of_code or 0
        total_classes += project.class_count or 0
    
    # Sort by lines of code (largest first)
    project_stats.sort(key=lambda x: x['lines_of_code'], reverse=True)
    
    # Get overall stats
    total_analyses = AnalysisHistory.query.filter_by(user_id=current_user.id).count()
    
    # Get analysis breakdown by type
    analysis_breakdown = db.session.query(
        AnalysisHistory.analysis_type,
        func.count(AnalysisHistory.id).label('count')
    ).filter_by(user_id=current_user.id).group_by(AnalysisHistory.analysis_type).all()
    
    analysis_by_type = {item[0]: item[1] for item in analysis_breakdown}
    
    return render_template(
        'stats/overview.html',
        projects=project_stats,
        total_projects=len(projects),
        total_files=total_files,
        total_functions=total_functions,
        total_lines=total_lines,
        total_classes=total_classes,
        total_analyses=total_analyses,
        analysis_by_type=analysis_by_type
    )


@stats.route('/project/<int:project_id>')
@login_required
def project_detail(project_id):
    """Detailed stats for a specific project"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    
    # Get all analyses for this project
    analyses = AnalysisHistory.query.filter_by(
        user_id=current_user.id,
        project_id=project_id
    ).order_by(AnalysisHistory.created_at.desc()).all()
    
    # Analysis timeline (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_analyses = AnalysisHistory.query.filter(
        AnalysisHistory.user_id == current_user.id,
        AnalysisHistory.project_id == project_id,
        AnalysisHistory.created_at >= thirty_days_ago
    ).order_by(AnalysisHistory.created_at.asc()).all()
    
    # Group by date
    timeline_data = {}
    for analysis in recent_analyses:
        date_key = analysis.created_at.strftime('%Y-%m-%d')
        timeline_data[date_key] = timeline_data.get(date_key, 0) + 1
    
    # Analysis breakdown by type
    analysis_breakdown = db.session.query(
        AnalysisHistory.analysis_type,
        func.count(AnalysisHistory.id).label('count')
    ).filter_by(
        user_id=current_user.id,
        project_id=project_id
    ).group_by(AnalysisHistory.analysis_type).all()
    
    analysis_by_type = {item[0]: item[1] for item in analysis_breakdown}
    
    # Calculate project health score (simple algorithm)
    health_score = 100
    if project.file_count:
        avg_lines_per_file = project.lines_of_code / project.file_count
        if avg_lines_per_file > 500:
            health_score -= 20
        if avg_lines_per_file > 1000:
            health_score -= 20
    
    # Check if recently analyzed
    if project.last_indexed:
        days_old = (datetime.utcnow() - project.last_indexed).days
        if days_old > 30:
            health_score -= 10
        if days_old > 90:
            health_score -= 20
    
    health_score = max(0, health_score)
    
    return render_template(
        'stats/project_detail.html',
        project=project,
        analyses=analyses[:20],  # Last 20 analyses
        timeline_data=timeline_data,
        analysis_by_type=analysis_by_type,
        health_score=health_score,
        total_analyses=len(analyses)
    )
