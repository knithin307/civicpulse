from flask import Blueprint, jsonify, request
from flask_login import current_user
from app.models.issue import Issue, IssueStatus, IssuePriority
from app.models.category import Category
from app.services.issue_service import IssueService
from app.services.analytics_service import AnalyticsService

api_bp = Blueprint('api', __name__)

@api_bp.route('/issues/geojson')
def get_issues_geojson():
    """
    Returns GeoJSON FeatureCollection of public civic issues for Leaflet map display.
    """
    category_id = request.args.get('category_id', type=int)
    department_id = request.args.get('department_id', type=int)
    status = request.args.get('status')
    priority = request.args.get('priority')
    
    query = Issue.query.filter_by(is_public=True)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    if department_id:
        query = query.filter_by(department_id=department_id)
    if status and status in IssueStatus.ALL:
        query = query.filter_by(status=status)
    if priority and priority in IssuePriority.ALL:
        query = query.filter_by(priority=priority)
        
    issues = query.all()
    
    features = [issue.to_geojson_feature() for issue in issues]
    
    return jsonify({
        'type': 'FeatureCollection',
        'features': features
    })

@api_bp.route('/issues/<int:issue_id>/upvote', methods=['POST'])
def upvote_issue(issue_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'Authentication required to upvote.'}), 401
        
    try:
        new_count, has_upvoted = IssueService.toggle_upvote(issue_id, current_user.id)
        return jsonify({
            'success': True,
            'upvotes_count': new_count,
            'has_upvoted': has_upvoted
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api_bp.route('/analytics/stats')
def get_analytics_stats():
    """
    Returns computed analytics and chart datasets for dynamic rendering.
    """
    summary = AnalyticsService.get_summary_stats()
    categories = AnalyticsService.get_category_breakdown()
    statuses = AnalyticsService.get_status_breakdown()
    priorities = AnalyticsService.get_priority_breakdown()
    trend = AnalyticsService.get_monthly_trend(6)
    
    return jsonify({
        'summary': summary,
        'categories': categories,
        'statuses': statuses,
        'priorities': priorities,
        'monthly_trend': trend
    })

@api_bp.route('/categories')
def get_categories():
    department_id = request.args.get('department_id', type=int)
    query = Category.query
    if department_id:
        query = query.filter_by(department_id=department_id)
        
    categories = query.all()
    return jsonify([c.to_dict() for c in categories])
