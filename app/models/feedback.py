from app.extensions import db
from app.utils.helpers import get_utc_now

class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id', ondelete='CASCADE'), unique=True, nullable=False)
    citizen_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    rating = db.Column(db.Integer, nullable=False) # 1 - 5 stars
    satisfaction = db.Column(db.String(20), default='satisfied', nullable=False) # satisfied, neutral, unsatisfied
    comments = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=get_utc_now, nullable=False)
    
    # Relationships
    issue = db.relationship('Issue', back_populates='feedback')
    citizen = db.relationship('User', back_populates='feedbacks')
    
    def to_dict(self):
        return {
            'id': self.id,
            'issue_id': self.issue_id,
            'citizen_name': self.citizen.full_name if self.citizen else 'Anonymous',
            'rating': self.rating,
            'satisfaction': self.satisfaction,
            'comments': self.comments,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }

    def __repr__(self):
        return f'<Feedback for Issue {self.issue_id}: {self.rating} stars>'
