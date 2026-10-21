from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.utils.helpers import get_utc_now

class UserRole:
    CITIZEN = 'citizen'
    OFFICER = 'officer'
    ADMIN = 'admin'
    
    ALL = [CITIZEN, OFFICER, ADMIN]

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(20), default=UserRole.CITIZEN, nullable=False, index=True)
    
    # If the user is an officer, link to their department
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='SET NULL'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=get_utc_now, nullable=False)
    is_active_user = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    department = db.relationship('Department', back_populates='officers', foreign_keys=[department_id])
    reported_issues = db.relationship('Issue', back_populates='citizen', foreign_keys='Issue.citizen_id', lazy='dynamic')
    resolved_issues = db.relationship('Issue', back_populates='resolved_by', foreign_keys='Issue.resolved_by_officer_id', lazy='dynamic')
    timeline_actions = db.relationship('IssueTimeline', back_populates='user', lazy='dynamic')
    feedbacks = db.relationship('Feedback', back_populates='citizen', lazy='dynamic')
    upvotes = db.relationship('IssueUpvote', back_populates='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN
        
    @property
    def is_officer(self):
        return self.role == UserRole.OFFICER
        
    @property
    def is_citizen(self):
        return self.role == UserRole.CITIZEN
        
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'role': self.role,
            'department_id': self.department_id,
            'department_name': self.department.name if self.department else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'
