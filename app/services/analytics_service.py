from datetime import datetime, timedelta
from sqlalchemy import func
from app.extensions import db
from app.models.issue import Issue, IssueStatus, IssuePriority
from app.models.department import Department
from app.models.category import Category
from app.models.feedback import Feedback
from app.utils.helpers import get_utc_now

class AnalyticsService:
    @staticmethod
    def get_summary_stats():
        """
        Computes real-time global KPI metrics directly from the database.
        """
        total = Issue.query.count()
        resolved = Issue.query.filter_by(status=IssueStatus.RESOLVED).count()
        in_progress = Issue.query.filter_by(status=IssueStatus.IN_PROGRESS).count()
        pending = Issue.query.filter(Issue.status.in_([IssueStatus.SUBMITTED, IssueStatus.UNDER_REVIEW])).count()
        rejected = Issue.query.filter_by(status=IssueStatus.REJECTED).count()
        
        resolution_rate = round((resolved / total * 100), 1) if total > 0 else 0.0
        
        # Calculate average resolution time for resolved issues
        resolved_issues = Issue.query.filter(
            Issue.status == IssueStatus.RESOLVED,
            Issue.resolved_at.isnot(None),
            Issue.created_at.isnot(None)
        ).all()
        
        sla_met_count = 0
        total_resolution_seconds = 0
        for issue in resolved_issues:
            delta = (issue.resolved_at - issue.created_at).total_seconds()
            total_resolution_seconds += max(0, delta)
            if not issue.is_sla_breached:
                sla_met_count += 1
                
        avg_resolution_hours = 0.0
        if resolved_issues:
            avg_resolution_hours = round((total_resolution_seconds / len(resolved_issues)) / 3600.0, 1)
            
        sla_compliance_rate = round((sla_met_count / len(resolved_issues) * 100), 1) if resolved_issues else 100.0
        
        # Citizen satisfaction rating
        rating_agg = db.session.query(
            func.avg(Feedback.rating),
            func.count(Feedback.id)
        ).first()
        
        avg_rating = round(float(rating_agg[0]), 1) if rating_agg and rating_agg[0] else 0.0
        feedback_count = rating_agg[1] if rating_agg and rating_agg[1] else 0
        
        # UN SDG 11 Urban Livability score (weighted metric based on real resolution rate, SLA compliance, and rating)
        # Scale: 0 to 100
        # Formula: 0.4 * resolution_rate + 0.3 * sla_compliance + 0.3 * (avg_rating / 5 * 100)
        livability_score = 0.0
        if total > 0:
            rating_percent = (avg_rating / 5.0) * 100.0 if avg_rating > 0 else 75.0
            livability_score = round(
                (0.45 * resolution_rate) + 
                (0.35 * sla_compliance_rate) + 
                (0.20 * rating_percent), 
                1
            )
            livability_score = min(100.0, max(0.0, livability_score))
        else:
            livability_score = 100.0
            
        return {
            'total_issues': total,
            'resolved_issues': resolved,
            'in_progress_issues': in_progress,
            'pending_issues': pending,
            'rejected_issues': rejected,
            'resolution_rate': resolution_rate,
            'avg_resolution_hours': avg_resolution_hours,
            'sla_compliance_rate': sla_compliance_rate,
            'avg_citizen_rating': avg_rating,
            'feedback_count': feedback_count,
            'livability_score': livability_score
        }

    @staticmethod
    def get_category_breakdown():
        """
        Returns real counts of issues grouped by category for Chart.js.
        """
        results = db.session.query(
            Category.name,
            func.count(Issue.id)
        ).outerjoin(Issue, Category.id == Issue.category_id)\
         .group_by(Category.id, Category.name)\
         .all()
         
        labels = [r[0] for r in results]
        data = [r[1] for r in results]
        
        return {'labels': labels, 'data': data}

    @staticmethod
    def get_status_breakdown():
        """
        Returns real counts of issues grouped by status.
        """
        status_order = [
            (IssueStatus.SUBMITTED, 'Submitted'),
            (IssueStatus.UNDER_REVIEW, 'Under Review'),
            (IssueStatus.IN_PROGRESS, 'In Progress'),
            (IssueStatus.RESOLVED, 'Resolved'),
            (IssueStatus.REJECTED, 'Rejected')
        ]
        
        labels = []
        data = []
        
        for code, label in status_order:
            count = Issue.query.filter_by(status=code).count()
            labels.append(label)
            data.append(count)
            
        return {'labels': labels, 'data': data}

    @staticmethod
    def get_priority_breakdown():
        """
        Returns real counts of issues grouped by priority.
        """
        priority_order = [
            (IssuePriority.LOW, 'Low'),
            (IssuePriority.MEDIUM, 'Medium'),
            (IssuePriority.HIGH, 'High'),
            (IssuePriority.CRITICAL, 'Critical')
        ]
        
        labels = []
        data = []
        for code, label in priority_order:
            count = Issue.query.filter_by(priority=code).count()
            labels.append(label)
            data.append(count)
            
        return {'labels': labels, 'data': data}

    @staticmethod
    def get_department_performance():
        """
        Returns department-wise performance statistics.
        """
        departments = Department.query.filter_by(is_active=True).all()
        dept_data = []
        
        for dept in departments:
            total_dept_issues = Issue.query.filter_by(department_id=dept.id).count()
            resolved_count = Issue.query.filter_by(department_id=dept.id, status=IssueStatus.RESOLVED).count()
            in_progress_count = Issue.query.filter_by(department_id=dept.id, status=IssueStatus.IN_PROGRESS).count()
            pending_count = Issue.query.filter(
                Issue.department_id == dept.id,
                Issue.status.in_([IssueStatus.SUBMITTED, IssueStatus.UNDER_REVIEW])
            ).count()
            
            rate = round((resolved_count / total_dept_issues * 100), 1) if total_dept_issues > 0 else 0.0
            
            # Avg resolution hours for this dept
            dept_resolved = Issue.query.filter(
                Issue.department_id == dept.id,
                Issue.status == IssueStatus.RESOLVED,
                Issue.resolved_at.isnot(None),
                Issue.created_at.isnot(None)
            ).all()
            
            dept_hours = 0.0
            if dept_resolved:
                total_sec = sum((i.resolved_at - i.created_at).total_seconds() for i in dept_resolved)
                dept_hours = round((total_sec / len(dept_resolved)) / 3600.0, 1)
                
            dept_data.append({
                'id': dept.id,
                'name': dept.name,
                'code': dept.code,
                'icon': dept.icon,
                'total_issues': total_dept_issues,
                'resolved_issues': resolved_count,
                'in_progress_issues': in_progress_count,
                'pending_issues': pending_count,
                'resolution_rate': rate,
                'avg_resolution_hours': dept_hours
            })
            
        return dept_data

    @staticmethod
    def get_monthly_trend(months_count=6):
        """
        Returns real issue creation vs resolution counts over the past N months.
        """
        now = get_utc_now()
        months = []
        created_counts = []
        resolved_counts = []
        
        for i in range(months_count - 1, -1, -1):
            # approximate month window
            target_date = now - timedelta(days=i * 30)
            month_label = target_date.strftime('%b %Y')
            start_date = datetime(target_date.year, target_date.month, 1)
            if target_date.month == 12:
                end_date = datetime(target_date.year + 1, 1, 1)
            else:
                end_date = datetime(target_date.year, target_date.month + 1, 1)
                
            created = Issue.query.filter(
                Issue.created_at >= start_date,
                Issue.created_at < end_date
            ).count()
            
            resolved = Issue.query.filter(
                Issue.status == IssueStatus.RESOLVED,
                Issue.resolved_at >= start_date,
                Issue.resolved_at < end_date
            ).count()
            
            months.append(month_label)
            created_counts.append(created)
            resolved_counts.append(resolved)
            
        return {
            'labels': months,
            'created': created_counts,
            'resolved': resolved_counts
        }
