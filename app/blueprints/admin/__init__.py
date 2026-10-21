from flask import Blueprint, render_template, request, flash, redirect, url_for, Response
from flask_login import login_required
from app.extensions import db
from app.models.user import User, UserRole
from app.models.department import Department
from app.models.category import Category
from app.models.issue import Issue, IssueStatus, IssuePriority
from app.services.analytics_service import AnalyticsService
from app.services.issue_service import IssueService
from app.utils.decorators import admin_required
import csv
import io

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    stats = AnalyticsService.get_summary_stats()
    dept_performance = AnalyticsService.get_department_performance()
    
    # Needs attention: Unassigned issues or SLA breached issues
    unassigned_issues = Issue.query.filter_by(department_id=None).all()
    recent_issues = Issue.query.order_by(Issue.created_at.desc()).limit(10).all()
    departments = Department.query.filter_by(is_active=True).all()
    
    return render_template(
        'admin/dashboard.html',
        stats=stats,
        dept_performance=dept_performance,
        unassigned_issues=unassigned_issues,
        recent_issues=recent_issues,
        departments=departments
    )

@admin_bp.route('/issues')
@login_required
@admin_required
def issues():
    status = request.args.get('status')
    department_id = request.args.get('department_id', type=int)
    category_id = request.args.get('category_id', type=int)
    search = request.args.get('q', '').strip()
    
    query = Issue.query
    
    if status and status in IssueStatus.ALL:
        query = query.filter_by(status=status)
    if department_id:
        query = query.filter_by(department_id=department_id)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if search:
        query = query.filter(
            (Issue.title.ilike(f"%{search}%")) |
            (Issue.tracking_id.ilike(f"%{search}%")) |
            (Issue.address.ilike(f"%{search}%"))
        )
        
    all_issues = query.order_by(Issue.created_at.desc()).all()
    departments = Department.query.all()
    categories = Category.query.all()
    
    return render_template(
        'admin/issues.html',
        issues=all_issues,
        departments=departments,
        categories=categories,
        selected_status=status,
        selected_department=department_id,
        selected_category=category_id,
        search_query=search
    )

@admin_bp.route('/issues/<int:issue_id>/assign', methods=['POST'])
@login_required
@admin_required
def assign_issue(issue_id):
    department_id = request.form.get('department_id', type=int)
    remarks = request.form.get('remarks', '').strip()
    
    if not department_id:
        flash('Please select a valid municipal department.', 'danger')
        return redirect(request.referrer or url_for('admin.issues'))
        
    from flask_login import current_user
    try:
        issue = IssueService.assign_department(issue_id, department_id, current_user, remarks=remarks)
        flash(f'Issue {issue.tracking_id} successfully assigned to {issue.department.name}.', 'success')
    except Exception as e:
        flash(f'Failed to assign department: {str(e)}', 'danger')
        
    return redirect(request.referrer or url_for('admin.issues'))

@admin_bp.route('/departments', methods=['GET', 'POST'])
@login_required
@admin_required
def departments():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        code = request.form.get('code', '').strip().upper()
        description = request.form.get('description', '').strip()
        contact_email = request.form.get('contact_email', '').strip()
        contact_phone = request.form.get('contact_phone', '').strip()
        icon = request.form.get('icon', 'bi-building').strip()
        
        if not name or not code:
            flash('Department Name and Code are required.', 'danger')
        else:
            existing = Department.query.filter((Department.name == name) | (Department.code == code)).first()
            if existing:
                flash('A department with this name or code already exists.', 'warning')
            else:
                dept = Department(
                    name=name,
                    code=code,
                    description=description,
                    contact_email=contact_email,
                    contact_phone=contact_phone,
                    icon=icon
                )
                db.session.add(dept)
                db.session.commit()
                flash(f'Department "{name}" created successfully.', 'success')
                return redirect(url_for('admin.departments'))
                
    departments_list = Department.query.all()
    return render_template('admin/departments.html', departments=departments_list)

@admin_bp.route('/users', methods=['GET', 'POST'])
@login_required
@admin_required
def users():
    if request.method == 'POST':
        user_id = request.form.get('user_id', type=int)
        role = request.form.get('role')
        department_id = request.form.get('department_id', type=int)
        
        user = User.query.get_or_404(user_id)
        if role in UserRole.ALL:
            user.role = role
            if role == UserRole.OFFICER:
                user.department_id = department_id
            else:
                user.department_id = None
            db.session.commit()
            flash(f'Updated user {user.full_name} ({user.email}) to role {role.capitalize()}.', 'success')
            return redirect(url_for('admin.users'))
            
    users_list = User.query.order_by(User.created_at.desc()).all()
    departments = Department.query.filter_by(is_active=True).all()
    return render_template('admin/users.html', users=users_list, departments=departments)

@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    stats = AnalyticsService.get_summary_stats()
    dept_performance = AnalyticsService.get_department_performance()
    return render_template('admin/analytics.html', stats=stats, dept_performance=dept_performance)

@admin_bp.route('/export/issues.csv')
@login_required
@admin_required
def export_csv():
    issues_list = Issue.query.order_by(Issue.created_at.desc()).all()
    
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow([
        'Tracking ID', 'Title', 'Category', 'Department', 'Status', 
        'Priority', 'Address', 'Latitude', 'Longitude', 'Created At', 
        'Resolved At', 'Resolution Hours', 'SLA Breached', 'Upvotes'
    ])
    
    for i in issues_list:
        writer.writerow([
            i.tracking_id,
            i.title,
            i.category.name if i.category else '',
            i.department.name if i.department else 'Unassigned',
            i.status,
            i.priority,
            i.address,
            i.latitude,
            i.longitude,
            i.created_at.strftime('%Y-%m-%d %H:%M:%S') if i.created_at else '',
            i.resolved_at.strftime('%Y-%m-%d %H:%M:%S') if i.resolved_at else '',
            i.resolution_hours or '',
            'Yes' if i.is_sla_breached else 'No',
            i.upvotes_count
        ])
        
    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=civicpulse_issues_report.csv"}
    )
