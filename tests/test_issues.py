from datetime import datetime
from app.models.issue import Issue, IssueStatus, IssuePriority, IssueTimeline
from app.models.feedback import Feedback
from app.services.issue_service import IssueService

def test_create_issue_service(app, db_session, sample_category, citizen_user):
    issue = IssueService.create_issue(
        title='Broken Manhole Lid on Oak St',
        description='Exposed opening in the middle of roadway.',
        category_id=sample_category.id,
        address='123 Oak St, North Ward',
        latitude=12.9800,
        longitude=77.6000,
        citizen_id=citizen_user.id,
        priority=IssuePriority.HIGH
    )
    
    assert issue.id is not None
    assert issue.tracking_id.startswith('CP-')
    assert issue.status == IssueStatus.SUBMITTED
    # Auto-assigned department from category
    assert issue.department_id == sample_category.department_id
    
    # Check timeline
    timelines = issue.timeline.all()
    assert len(timelines) == 1
    assert timelines[0].new_status == IssueStatus.SUBMITTED

def test_update_status_and_timeline(app, db_session, sample_category, officer_user):
    issue = IssueService.create_issue(
        title='Water leak',
        description='Test leak',
        category_id=sample_category.id,
        address='Main Road',
        latitude=12.9,
        longitude=77.5
    )
    
    updated_issue = IssueService.update_status(
        issue.id,
        IssueStatus.IN_PROGRESS,
        user=officer_user,
        remarks='Squad 4 dispatched.'
    )
    
    assert updated_issue.status == IssueStatus.IN_PROGRESS
    timelines = updated_issue.timeline.all()
    assert len(timelines) == 2
    assert timelines[1].new_status == IssueStatus.IN_PROGRESS
    assert 'Squad 4 dispatched' in timelines[1].remarks

def test_resolve_issue_with_evidence(app, db_session, sample_category, officer_user):
    issue = IssueService.create_issue(
        title='Streetlight dark',
        description='Broken bulb',
        category_id=sample_category.id,
        address='Cross Road 2',
        latitude=12.95,
        longitude=77.55
    )
    
    resolved_issue = IssueService.resolve_issue(
        issue_id=issue.id,
        officer_user=officer_user,
        resolution_notes='Replaced 60W LED unit and reconnected cable.',
        image_after='uploads/resolutions/test_after.svg'
    )
    
    assert resolved_issue.status == IssueStatus.RESOLVED
    assert resolved_issue.resolved_at is not None
    assert resolved_issue.resolved_by_officer_id == officer_user.id
    assert resolved_issue.image_after == 'uploads/resolutions/test_after.svg'

def test_toggle_upvotes(app, db_session, sample_category, citizen_user):
    issue = IssueService.create_issue(
        title='Dangerous crater',
        description='Urgent hazard',
        category_id=sample_category.id,
        address='South Way',
        latitude=12.92,
        longitude=77.58
    )
    
    # First upvote
    count1, has_upvoted1 = IssueService.toggle_upvote(issue.id, citizen_user.id)
    assert count1 == 1
    assert has_upvoted1 is True
    
    # Toggle again -> removes upvote
    count2, has_upvoted2 = IssueService.toggle_upvote(issue.id, citizen_user.id)
    assert count2 == 0
    assert has_upvoted2 is False
