from app.extensions import db
from app.utils.helpers import get_utc_now

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    icon = db.Column(db.String(50), default='bi-exclamation-triangle', nullable=False)
    default_severity = db.Column(db.String(20), default='medium', nullable=False)
    sla_hours = db.Column(db.Integer, default=48, nullable=False)
    
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now, nullable=False)
    
    # Relationships
    department = db.relationship('Department', back_populates='categories')
    issues = db.relationship('Issue', back_populates='category', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'default_severity': self.default_severity,
            'sla_hours': self.sla_hours,
            'department_id': self.department_id,
            'department_name': self.department.name if self.department else None
        }

    def __repr__(self):
        return f'<Category {self.name}>'
