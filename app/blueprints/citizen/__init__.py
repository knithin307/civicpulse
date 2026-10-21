from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.issue import Issue, IssueStatus, IssuePriority
from app.models.category import Category
from app.models.feedback import Feedback
from app.services.issue_service import IssueService
from app.utils.decorators import citizen_required
from app.utils.file_upload import save_uploaded_file

citizen_bp = Blueprint('citizen', __name__)

@citizen_bp.route('/dashboard')
@login_required
@citizen_required
def dashboard():
    user_issues = Issue.query.filter_by(citizen_id=current_user.id)\
                             .order_by(Issue.created_at.desc()).all()
                             
    total_count = len(user_issues)
    resolved_count = sum(1 for i in user_issues if i.status == IssueStatus.RESOLVED)
    in_progress_count = sum(1 for i in user_issues if i.status == IssueStatus.IN_PROGRESS)
    pending_count = sum(1 for i in user_issues if i.status in [IssueStatus.SUBMITTED, IssueStatus.UNDER_REVIEW])
    
    return render_template(
        'citizen/dashboard.html',
        issues=user_issues[:5],
        total_count=total_count,
        resolved_count=resolved_count,
        in_progress_count=in_progress_count,
        pending_count=pending_count
    )

@citizen_bp.route('/reports')
@login_required
@citizen_required
def my_reports():
    status = request.args.get('status')
    query = Issue.query.filter_by(citizen_id=current_user.id)
    
    if status and status in IssueStatus.ALL:
        query = query.filter_by(status=status)
        
    issues = query.order_by(Issue.created_at.desc()).all()
    return render_template('citizen/my_reports.html', issues=issues, selected_status=status)

@citizen_bp.route('/report/new', methods=['GET', 'POST'])
@login_required
@citizen_required
def report_issue():
    categories = Category.query.all()
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category_id = request.form.get('category_id', type=int)
        priority = request.form.get('priority', IssuePriority.MEDIUM)
        address = request.form.get('address', '').strip()
        lat = request.form.get('latitude', type=float)
        lng = request.form.get('longitude', type=float)
        is_public = bool(request.form.get('is_public', True))
        
        if not title or not description or not category_id or not address or lat is None or lng is None:
            flash('Please complete all required fields and pinpoint the location on the map.', 'danger')
            return render_template('citizen/report_issue.html', categories=categories)
            
        # Handle photo upload
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                try:
                    image_url = save_uploaded_file(file, subfolder='issues')
                except ValueError as e:
                    flash(str(e), 'danger')
                    return render_template('citizen/report_issue.html', categories=categories)
                    
        try:
            issue = IssueService.create_issue(
                title=title,
                description=description,
                category_id=category_id,
                address=address,
                latitude=lat,
                longitude=lng,
                citizen_id=current_user.id,
                priority=priority,
                image_before=image_url,
                is_public=is_public
            )
            flash(f'Issue reported successfully! Your Tracking ID is {issue.tracking_id}', 'success')
            return redirect(url_for('citizen.issue_detail', issue_id=issue.id))
        except Exception as e:
            flash(f'Error creating report: {str(e)}', 'danger')
            
    return render_template('citizen/report_issue.html', categories=categories)

@citizen_bp.route('/reports/<int:issue_id>')
def issue_detail(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    
    # If not public and user is not owner, officer, or admin, deny access
    if not issue.is_public:
        if not current_user.is_authenticated:
            abort(403)
        if current_user.id != issue.citizen_id and not current_user.is_officer and not current_user.is_admin:
            abort(403)
            
    user_upvoted = False
    if current_user.is_authenticated:
        user_upvoted = issue.upvotes.filter_by(user_id=current_user.id).first() is not None
        
    return render_template(
        'citizen/issue_detail.html',
        issue=issue,
        user_upvoted=user_upvoted
    )

@citizen_bp.route('/reports/<int:issue_id>/feedback', methods=['POST'])
@login_required
@citizen_required
def submit_feedback(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    
    # Only reporting citizen or admin can submit feedback on their own issue
    if current_user.id != issue.citizen_id and not current_user.is_admin:
        flash('You can only submit feedback for issues you reported.', 'danger')
        return redirect(url_for('citizen.issue_detail', issue_id=issue.id))
        
    if issue.status != IssueStatus.RESOLVED:
        flash('Feedback can only be provided after an issue is resolved.', 'warning')
        return redirect(url_for('citizen.issue_detail', issue_id=issue.id))
        
    if issue.feedback:
        flash('You have already submitted feedback for this issue. Thank you!', 'info')
        return redirect(url_for('citizen.issue_detail', issue_id=issue.id))
        
    rating = request.form.get('rating', type=int)
    satisfaction = request.form.get('satisfaction', 'satisfied')
    comments = request.form.get('comments', '').strip()
    
    if not rating or rating < 1 or rating > 5:
        flash('Please select a star rating between 1 and 5.', 'danger')
        return redirect(url_for('citizen.issue_detail', issue_id=issue.id))
        
    feedback = Feedback(
        issue_id=issue.id,
        citizen_id=current_user.id,
        rating=rating,
        satisfaction=satisfaction,
        comments=comments
    )
    db.session.add(feedback)
    db.session.commit()
    
    flash('Thank you for rating our municipal resolution service!', 'success')
    return redirect(url_for('citizen.issue_detail', issue_id=issue.id))
