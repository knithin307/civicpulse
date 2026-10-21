from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.models.issue import Issue, IssueStatus, IssuePriority
from app.models.category import Category
from app.models.department import Department
from app.services.analytics_service import AnalyticsService

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    stats = AnalyticsService.get_summary_stats()
    
    # 4 most recent resolved issues with before/after pictures for proof of resolution showcase
    recent_resolved = Issue.query.filter_by(status=IssueStatus.RESOLVED)\
                                 .order_by(Issue.resolved_at.desc())\
                                 .limit(4).all()
                                 
    # Recent public issues
    recent_issues = Issue.query.filter_by(is_public=True)\
                               .order_by(Issue.created_at.desc())\
                               .limit(6).all()
                               
    departments = Department.query.filter_by(is_active=True).all()
    categories = Category.query.all()
    
    return render_template(
        'main/index.html',
        stats=stats,
        recent_resolved=recent_resolved,
        recent_issues=recent_issues,
        departments=departments,
        categories=categories
    )

@main_bp.route('/explore')
def explore():
    category_id = request.args.get('category_id', type=int)
    department_id = request.args.get('department_id', type=int)
    status = request.args.get('status')
    priority = request.args.get('priority')
    search = request.args.get('q', '').strip()
    
    query = Issue.query.filter_by(is_public=True)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    if department_id:
        query = query.filter_by(department_id=department_id)
    if status and status in IssueStatus.ALL:
        query = query.filter_by(status=status)
    if priority and priority in IssuePriority.ALL:
        query = query.filter_by(priority=priority)
    if search:
        query = query.filter(
            (Issue.title.ilike(f"%{search}%")) |
            (Issue.description.ilike(f"%{search}%")) |
            (Issue.address.ilike(f"%{search}%")) |
            (Issue.tracking_id.ilike(f"%{search}%"))
        )
        
    issues = query.order_by(Issue.created_at.desc()).all()
    categories = Category.query.all()
    departments = Department.query.filter_by(is_active=True).all()
    
    return render_template(
        'main/explore.html',
        issues=issues,
        categories=categories,
        departments=departments,
        selected_category=category_id,
        selected_department=department_id,
        selected_status=status,
        selected_priority=priority,
        search_query=search
    )

@main_bp.route('/track', methods=['GET', 'POST'])
def track():
    tracking_id = request.args.get('tracking_id') or request.form.get('tracking_id')
    issue = None
    
    if tracking_id:
        tracking_id = tracking_id.strip().upper()
        issue = Issue.query.filter_by(tracking_id=tracking_id).first()
        if not issue:
            flash(f'No civic issue found with Tracking ID: {tracking_id}. Please check the code and try again.', 'warning')
            
    return render_template('main/track.html', issue=issue, tracking_id=tracking_id)

@main_bp.route('/about-sdg11')
def sdg11():
    stats = AnalyticsService.get_summary_stats()
    return render_template('main/sdg11.html', stats=stats)
