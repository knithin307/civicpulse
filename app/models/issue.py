import random
import string
from datetime import timedelta
from app.extensions import db
from app.utils.helpers import get_utc_now

class IssueStatus:
    SUBMITTED = 'submitted'
    UNDER_REVIEW = 'under_review'
    IN_PROGRESS = 'in_progress'
    RESOLVED = 'resolved'
    REJECTED = 'rejected'
    
    ALL = [SUBMITTED, UNDER_REVIEW, IN_PROGRESS, RESOLVED, REJECTED]
    
    BADGE_MAP = {
        SUBMITTED: {'bg': 'warning', 'text': 'dark', 'label': 'Submitted'},
        UNDER_REVIEW: {'bg': 'info', 'text': 'dark', 'label': 'Under Review'},
        IN_PROGRESS: {'bg': 'primary', 'text': 'white', 'label': 'In Progress'},
        RESOLVED: {'bg': 'success', 'text': 'white', 'label': 'Resolved'},
        REJECTED: {'bg': 'danger', 'text': 'white', 'label': 'Rejected'}
    }

class IssuePriority:
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'
    
    ALL = [LOW, MEDIUM, HIGH, CRITICAL]
    
    BADGE_MAP = {
        LOW: {'bg': 'secondary', 'label': 'Low'},
        MEDIUM: {'bg': 'info', 'label': 'Medium'},
        HIGH: {'bg': 'warning', 'label': 'High'},
        CRITICAL: {'bg': 'danger', 'label': 'Critical'}
    }

def generate_tracking_id():
    now = get_utc_now()
    rand_chars = ''.join(random.choices(string.digits, k=5))
    return f"CP-{now.year}-{rand_chars}"

class Issue(db.Model):
    __tablename__ = 'issues'
    
    id = db.Column(db.Integer, primary_key=True)
    tracking_id = db.Column(db.String(30), unique=True, nullable=False, index=True, default=generate_tracking_id)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Classification
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='RESTRICT'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='SET NULL'), nullable=True)
    
    # Reporter
    citizen_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    # Status and priority
    status = db.Column(db.String(30), default=IssueStatus.SUBMITTED, nullable=False, index=True)
    priority = db.Column(db.String(20), default=IssuePriority.MEDIUM, nullable=False)
    
    # Geospatial details
    address = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    
    # Evidence & Media
    image_before = db.Column(db.String(255), nullable=True)
    image_after = db.Column(db.String(255), nullable=True) # Resolution evidence
    resolution_notes = db.Column(db.Text, nullable=True)
    resolved_by_officer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    # Timestamps & SLA
    created_at = db.Column(db.DateTime, default=get_utc_now, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    upvotes_count = db.Column(db.Integer, default=0, nullable=False)
    is_public = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    category = db.relationship('Category', back_populates='issues')
    department = db.relationship('Department', back_populates='issues')
    citizen = db.relationship('User', back_populates='reported_issues', foreign_keys=[citizen_id])
    resolved_by = db.relationship('User', back_populates='resolved_issues', foreign_keys=[resolved_by_officer_id])
    timeline = db.relationship('IssueTimeline', back_populates='issue', cascade='all, delete-orphan', order_by='IssueTimeline.created_at.asc()', lazy='dynamic')
    feedback = db.relationship('Feedback', back_populates='issue', uselist=False, cascade='all, delete-orphan')
    upvotes = db.relationship('IssueUpvote', back_populates='issue', cascade='all, delete-orphan', lazy='dynamic')
    
    @property
    def is_resolved(self):
        return self.status == IssueStatus.RESOLVED
        
    @property
    def sla_deadline(self):
        if self.category and self.category.sla_hours:
            return self.created_at + timedelta(hours=self.category.sla_hours)
        return self.created_at + timedelta(hours=48)
        
    @property
    def is_sla_breached(self):
        if self.is_resolved:
            return self.resolved_at > self.sla_deadline if self.resolved_at else False
        return get_utc_now() > self.sla_deadline

    @property
    def resolution_hours(self):
        if self.resolved_at and self.created_at:
            delta = self.resolved_at - self.created_at
            return round(delta.total_seconds() / 3600.0, 1)
        return None

    def to_geojson_feature(self):
        return {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [self.longitude, self.latitude]
            },
            'properties': {
                'id': self.id,
                'tracking_id': self.tracking_id,
                'title': self.title,
                'category': self.category.name if self.category else 'General',
                'department': self.department.name if self.department else 'Unassigned',
                'status': self.status,
                'priority': self.priority,
                'address': self.address,
                'image_before': self.image_before,
                'image_after': self.image_after,
                'created_at': self.created_at.strftime('%Y-%m-%d %H:%M'),
                'upvotes_count': self.upvotes_count
            }
        }

    def __repr__(self):
        return f'<Issue {self.tracking_id} - {self.status}>'


class IssueTimeline(db.Model):
    __tablename__ = 'issue_timelines'
    
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    action = db.Column(db.String(80), nullable=False)
    old_status = db.Column(db.String(30), nullable=True)
    new_status = db.Column(db.String(30), nullable=True)
    remarks = db.Column(db.Text, nullable=True)
    is_public = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now, nullable=False)
    
    # Relationships
    issue = db.relationship('Issue', back_populates='timeline')
    user = db.relationship('User', back_populates='timeline_actions')
    
    def __repr__(self):
        return f'<IssueTimeline {self.issue_id}: {self.action}>'


class IssueUpvote(db.Model):
    __tablename__ = 'issue_upvotes'
    __table_args__ = (
        db.UniqueConstraint('issue_id', 'user_id', name='uq_issue_user_upvote'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now, nullable=False)
    
    # Relationships
    issue = db.relationship('Issue', back_populates='upvotes')
    user = db.relationship('User', back_populates='upvotes')
