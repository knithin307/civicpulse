import os
from flask import Flask, render_template
from app.config import config_by_name
from app.extensions import db, login_manager
from app.models.user import User
from app.models.issue import IssueStatus, IssuePriority

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))
    
    # Initialize Extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # User loader callback
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
        
    # Ensure upload folders exist
    os.makedirs(app.config.get('ISSUES_UPLOAD_FOLDER', os.path.join(app.root_path, 'static', 'uploads', 'issues')), exist_ok=True)
    os.makedirs(app.config.get('RESOLUTIONS_UPLOAD_FOLDER', os.path.join(app.root_path, 'static', 'uploads', 'resolutions')), exist_ok=True)
    
    # Register Template Filters and Context Processors
    @app.context_processor
    def inject_global_template_vars():
        return {
            'issue_statuses': IssueStatus,
            'issue_priorities': IssuePriority,
            'status_badges': IssueStatus.BADGE_MAP,
            'priority_badges': IssuePriority.BADGE_MAP,
            'app_name': 'CivicPulse',
            'sdg_goal': 'SDG 11: Sustainable Cities & Communities'
        }
        
    @app.template_filter('datetime_format')
    def datetime_format_filter(value, format='%b %d, %Y %I:%M %p'):
        if value is None:
            return '—'
        return value.strftime(format)
        
    @app.template_filter('date_format')
    def date_format_filter(value, format='%b %d, %Y'):
        if value is None:
            return '—'
        return value.strftime(format)
        
    # Register Blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.main import main_bp
    from app.blueprints.citizen import citizen_bp
    from app.blueprints.officer import officer_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.api import api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp, url_prefix='/')
    app.register_blueprint(citizen_bp, url_prefix='/citizen')
    app.register_blueprint(officer_bp, url_prefix='/officer')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # Error Handlers
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app
