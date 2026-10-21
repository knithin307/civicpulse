from app.extensions import db
from app.models.issue import Issue, IssueTimeline, IssueStatus, IssuePriority, IssueUpvote
from app.models.category import Category
from app.utils.helpers import get_utc_now

class IssueService:
    @staticmethod
    def create_issue(title, description, category_id, address, latitude, longitude,
                     citizen_id=None, priority=None, image_before=None, is_public=True):
        """
        Creates a new issue and sets up initial timeline event.
        Auto-assigns department from category.
        """
        category = db.session.get(Category, category_id)
        if not category:
            raise ValueError(f"Category with ID {category_id} not found.")
            
        final_priority = priority or category.default_severity or IssuePriority.MEDIUM
        department_id = category.department_id
        
        issue = Issue(
            title=title.strip(),
            description=description.strip(),
            category_id=category_id,
            department_id=department_id,
            citizen_id=citizen_id,
            status=IssueStatus.SUBMITTED,
            priority=final_priority,
            address=address.strip(),
            latitude=float(latitude),
            longitude=float(longitude),
            image_before=image_before,
            is_public=is_public
        )
        
        db.session.add(issue)
        db.session.flush() # Populate issue.id and issue.tracking_id
        
        # Initial timeline record
        timeline_entry = IssueTimeline(
            issue_id=issue.id,
            user_id=citizen_id,
            action='Issue Reported',
            old_status=None,
            new_status=IssueStatus.SUBMITTED,
            remarks='Citizen submitted civic issue report with location and details.',
            is_public=True
        )
        db.session.add(timeline_entry)
        db.session.commit()
        return issue

    @staticmethod
    def update_status(issue_id, new_status, user, remarks=None):
        """
        Transitions issue status and logs timeline audit.
        """
        if new_status not in IssueStatus.ALL:
            raise ValueError(f"Invalid status: {new_status}")
            
        issue = db.get_or_404(Issue, issue_id)
        old_status = issue.status
        
        if old_status == new_status:
            return issue
            
        issue.status = new_status
        issue.updated_at = get_utc_now()
        
        if new_status == IssueStatus.RESOLVED:
            issue.resolved_at = get_utc_now()
            if user and user.is_officer:
                issue.resolved_by_officer_id = user.id
                
        timeline = IssueTimeline(
            issue_id=issue.id,
            user_id=user.id if user else None,
            action=f"Status changed to {IssueStatus.BADGE_MAP.get(new_status, {}).get('label', new_status)}",
            old_status=old_status,
            new_status=new_status,
            remarks=remarks or f"Status updated by {user.full_name if user else 'System'}.",
            is_public=True
        )
        
        db.session.add(timeline)
        db.session.commit()
        return issue

    @staticmethod
    def resolve_issue(issue_id, officer_user, resolution_notes, image_after=None):
        """
        Submits resolution proof and marks issue as resolved.
        """
        issue = db.get_or_404(Issue, issue_id)
        old_status = issue.status
        
        issue.status = IssueStatus.RESOLVED
        issue.resolved_at = get_utc_now()
        issue.resolved_by_officer_id = officer_user.id
        issue.resolution_notes = resolution_notes.strip() if resolution_notes else "Resolution completed."
        
        if image_after:
            issue.image_after = image_after
            
        issue.updated_at = get_utc_now()
        
        timeline = IssueTimeline(
            issue_id=issue.id,
            user_id=officer_user.id,
            action="Resolution Completed & Evidence Submitted",
            old_status=old_status,
            new_status=IssueStatus.RESOLVED,
            remarks=resolution_notes,
            is_public=True
        )
        
        db.session.add(timeline)
        db.session.commit()
        return issue

    @staticmethod
    def assign_department(issue_id, department_id, admin_user, remarks=None):
        """
        Reassigns an issue to a specific department.
        """
        issue = db.get_or_404(Issue, issue_id)
        old_dept_name = issue.department.name if issue.department else 'Unassigned'
        
        issue.department_id = department_id
        issue.updated_at = get_utc_now()
        
        new_dept_name = issue.department.name if issue.department else 'Department'
        action_msg = f"Reassigned to {new_dept_name}"
        
        timeline = IssueTimeline(
            issue_id=issue.id,
            user_id=admin_user.id,
            action=action_msg,
            old_status=issue.status,
            new_status=issue.status,
            remarks=remarks or f"Reassigned from {old_dept_name} to {new_dept_name} by municipal administrator.",
            is_public=True
        )
        
        db.session.add(timeline)
        db.session.commit()
        return issue

    @staticmethod
    def toggle_upvote(issue_id, user_id):
        """
        Allows a user to toggle an upvote on an issue.
        Returns (new_count, has_upvoted).
        """
        issue = db.get_or_404(Issue, issue_id)
        existing = IssueUpvote.query.filter_by(issue_id=issue_id, user_id=user_id).first()
        
        if existing:
            db.session.delete(existing)
            issue.upvotes_count = max(0, issue.upvotes_count - 1)
            has_upvoted = False
        else:
            upvote = IssueUpvote(issue_id=issue_id, user_id=user_id)
            db.session.add(upvote)
            issue.upvotes_count += 1
            has_upvoted = True
            
        db.session.commit()
        return issue.upvotes_count, has_upvoted
