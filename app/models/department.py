from app.extensions import db
from app.utils.helpers import get_utc_now

class Department(db.Model):
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    contact_email = db.Column(db.String(120), nullable=True)
    contact_phone = db.Column(db.String(30), nullable=True)
    icon = db.Column(db.String(50), default='bi-building', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now, nullable=False)
    
    # Relationships
    officers = db.relationship('User', back_populates='department', lazy='dynamic')
    categories = db.relationship('Category', back_populates='department', cascade='all, delete-orphan', lazy='dynamic')
    issues = db.relationship('Issue', back_populates='department', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'icon': self.icon,
            'is_active': self.is_active,
            'officers_count': self.officers.count(),
            'open_issues_count': self.issues.filter_by(status='in_progress').count()
        }

    def __repr__(self):
        return f'<Department {self.name} ({self.code})>'
