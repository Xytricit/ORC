"""
Projects management routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from orc.web.models import db, Project
from orc.web.forms import ProjectForm
from datetime import datetime
from pathlib import Path
import os

projects = Blueprint('projects', __name__, url_prefix='/projects')


@projects.route('/')
@login_required
def list():
    """List all user projects"""
    user_projects = Project.query.filter_by(user_id=current_user.id).order_by(Project.updated_at.desc()).all()
    return render_template('projects/list.html', projects=user_projects)


@projects.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Create new project"""
    form = ProjectForm()
    
    if form.validate_on_submit():
        # Validate path exists
        project_path = Path(form.path.data)
        if not project_path.exists():
            flash('Project path does not exist.', 'error')
            return render_template('projects/new.html', form=form)
        
        # Create project
        project = Project(
            user_id=current_user.id,
            name=form.name.data,
            path=str(project_path.resolve()),
            description=form.description.data,
            db_path=str(project_path / '.orc' / 'index.db')
        )
        
        try:
            db.session.add(project)
            db.session.commit()
            flash(f'Project "{project.name}" created successfully!', 'success')
            return redirect(url_for('projects.detail', project_id=project.id))
        except Exception as e:
            db.session.rollback()
            flash('Error creating project. Please try again.', 'error')
            print(f"Error creating project: {e}")
    
    return render_template('projects/new.html', form=form)


@projects.route('/<int:project_id>')
@login_required
def detail(project_id):
    """Project detail view"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    
    # Get project statistics from database if indexed
    stats = {
        'files': project.file_count or 0,
        'functions': project.function_count or 0,
        'classes': project.class_count or 0,
        'lines_of_code': project.lines_of_code or 0,
        'last_indexed': project.last_indexed,
        'is_indexed': project.last_indexed is not None
    }
    
    return render_template('projects/detail.html', project=project, stats=stats)


@projects.route('/<int:project_id>/index', methods=['POST'])
@login_required
def index_project(project_id):
    """Index or re-index a project"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    
    try:
        # Import ORC indexer
        from orc.core.parallel_indexer import index_directory_parallel
        from orc.storage.graph_db import GraphDatabase
        
        project_path = Path(project.path)
        db_path = Path(project.db_path)
        
        # Create .orc directory if needed
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Run indexer
        result = index_directory_parallel(project_path)
        
        # Save to database
        graph_db = GraphDatabase(str(db_path))
        
        # Store files
        for file_path, file_info in result.get('files', {}).items():
            graph_db.add_file(
                file_path=file_path,
                language=file_info.get('language', 'unknown'),
                size=file_info.get('loc', 0)
            )
        
        # Store functions
        for func_name, func_info in result.get('functions', {}).items():
            graph_db.add_function(
                name=func_name,
                file_path=func_info.get('file_path', ''),
                start_line=func_info.get('start_line', 0),
                end_line=func_info.get('end_line', 0),
                complexity=func_info.get('complexity', 1),
                params=func_info.get('params', [])
            )
        
        # Store classes
        for class_name, class_info in result.get('classes', {}).items():
            graph_db.add_class(
                name=class_name,
                file_path=class_info.get('file_path', ''),
                start_line=class_info.get('start_line', 0),
                end_line=class_info.get('end_line', 0),
                methods=class_info.get('methods', [])
            )
        
        graph_db.connection.commit()
        
        # Update project stats
        project.file_count = len(result.get('files', {}))
        project.function_count = len(result.get('functions', {}))
        project.class_count = len(result.get('classes', {}))
        project.last_indexed = datetime.utcnow()
        
        db.session.commit()
        
        flash(f'Project indexed successfully! Found {project.file_count} files, {project.function_count} functions.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error indexing project: {str(e)}', 'error')
        print(f"Indexing error: {e}")
    
    return redirect(url_for('projects.detail', project_id=project.id))


@projects.route('/<int:project_id>/delete', methods=['POST'])
@login_required
def delete(project_id):
    """Delete a project"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    
    try:
        project_name = project.name
        db.session.delete(project)
        db.session.commit()
        flash(f'Project "{project_name}" deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting project. Please try again.', 'error')
        print(f"Error deleting project: {e}")
    
    return redirect(url_for('projects.list'))
