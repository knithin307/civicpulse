from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from app.models.issue import Issue, IssueStatus, IssuePriority
from app.services.issue_service import IssueService
from app.utils.decorators import officer_required
from app.utils.file_upload import save_uploaded_file

officer_bp = Blueprint('officer', __name__)

@officer_bp.route('/dashboard')
@login_required
@officer_required
def dashboard():
    department = current_user.department
    
    # Query issues for officer's department (or all if admin acting as officer)
    if department:
        query = Issue.query.filter_by(department_id=department.id)
    else:
        query = Issue.query
        
    status_filter = request.args.get('status')
    priority_filter = request.args.get('priority')
    
    if status_filter and status_filter in IssueStatus.ALL:
        query = query.filter_by(status=status_filter)
    if priority_filter and priority_filter in IssuePriority.ALL:
        query = query.filter_by(priority=priority_filter)
        
    issues = query.order_by(Issue.created_at.desc()).all()
    
    # Calculate real department metrics
    if department:
        all_dept_issues = Issue.query.filter_by(department_id=department.id).all()
    else:
        all_dept_issues = Issue.query.all()
        
    total_count = len(all_dept_issues)
    submitted_count = sum(1 for i in all_dept_issues if i.status == IssueStatus.SUBMITTED)
    in_progress_count = sum(1 for i in all_dept_issues if i.status == IssueStatus.IN_PROGRESS)
    resolved_count = sum(1 for i in all_dept_issues if i.status == IssueStatus.RESOLVED)
    breached_count = sum(1 for i in all_dept_issues if i.is_sla_breached and i.status != IssueStatus.RESOLVED)
    
    return render_template(
        'officer/dashboard.html',
        department=department,
        issues=issues,
        total_count=total_count,
        submitted_count=submitted_count,
        in_progress_count=in_progress_count,
        resolved_count=resolved_count,
        breached_count=breached_count,
        selected_status=status_filter,
        selected_priority=priority_filter
    )

@officer_bp.route('/issues/<int:issue_id>/update-status', methods=['POST'])
@login_required
@officer_required
def update_status(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    new_status = request.form.get('status')
    remarks = request.form.get('remarks', '').strip()
    
    # Check department access: officer can only manage their department's issues (unless admin)
    if not current_user.is_admin and current_user.department_id and issue.department_id != current_user.department_id:
        flash('You are only authorized to manage issues belonging to your department.', 'danger')
        return redirect(url_for('officer.dashboard'))
        
    if new_status not in IssueStatus.ALL:
        flash('Invalid status selected.', 'danger')
        return redirect(url_for('officer.dashboard'))
        
    # If transitioning to resolved, redirect to resolution proof upload form
    if new_status == IssueStatus.RESOLVED:
        return redirect(url_for('officer.resolve_issue', issue_id=issue.id))
        
    try:
        IssueService.update_status(issue.id, new_status, current_user, remarks=remarks)
        flash(f'Issue {issue.tracking_id} updated to {IssueStatus.BADGE_MAP[new_status]["label"]}.', 'success')
    except Exception as e:
        flash(f'Failed to update status: {str(e)}', 'danger')
        
    return redirect(url_for('officer.dashboard'))

@officer_bp.route('/issues/<int:issue_id>/resolve', methods=['GET', 'POST'])
@login_required
@officer_required
def resolve_issue(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    
    if not current_user.is_admin and current_user.department_id and issue.department_id != current_user.department_id:
        flash('You are only authorized to resolve issues belonging to your department.', 'danger')
        return redirect(url_for('officer.dashboard'))
        
    if request.method == 'POST':
        resolution_notes = request.form.get('resolution_notes', '').strip()
        
        if not resolution_notes:
            flash('Please describe the work performed and corrective measures taken.', 'danger')
            return render_template('officer/resolve_issue.html', issue=issue)
            
        # Optional or required resolution proof photo
        image_after_url = None
        if 'image_after' in request.files:
            file = request.files['image_after']
            if file and file.filename != '':
                try:
                    image_after_url = save_uploaded_file(file, subfolder='resolutions')
                except ValueError as e:
                    flash(str(e), 'danger')
                    return render_template('officer/resolve_issue.html', issue=issue)
                    
        try:
            IssueService.resolve_issue(
                issue_id=issue.id,
                officer_user=current_user,
                resolution_notes=resolution_notes,
                image_after=image_after_url
            )
            flash(f'Issue {issue.tracking_id} successfully marked as RESOLVED with resolution evidence!', 'success')
            return redirect(url_for('officer.dashboard'))
        except Exception as e:
            flash(f'Error resolving issue: {str(e)}', 'danger')
            
    return render_template('officer/resolve_issue.html', issue=issue)
