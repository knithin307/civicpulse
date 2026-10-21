from tests.conftest import login
from app.services.issue_service import IssueService

def test_api_geojson_issues(client, sample_category, citizen_user):
    IssueService.create_issue(
        title='Geo Point 1',
        description='Desc 1',
        category_id=sample_category.id,
        address='Addr 1',
        latitude=12.97,
        longitude=77.59,
        citizen_id=citizen_user.id
    )
    
    response = client.get('/api/v1/issues/geojson')
    assert response.status_code == 200
    data = response.get_json()
    assert data['type'] == 'FeatureCollection'
    assert len(data['features']) >= 1
    feat = data['features'][0]
    assert feat['geometry']['type'] == 'Point'
    assert feat['properties']['title'] == 'Geo Point 1'

def test_api_analytics_stats(client, sample_category):
    IssueService.create_issue(
        title='Stat Issue 1',
        description='Desc',
        category_id=sample_category.id,
        address='Addr',
        latitude=12.95,
        longitude=77.55
    )
    
    response = client.get('/api/v1/analytics/stats')
    assert response.status_code == 200
    data = response.get_json()
    assert 'summary' in data
    assert 'categories' in data
    assert 'statuses' in data
    assert data['summary']['total_issues'] >= 1

def test_api_upvote_auth_required(client, sample_category):
    issue = IssueService.create_issue(
        title='Needs Upvote',
        description='Desc',
        category_id=sample_category.id,
        address='Addr',
        latitude=12.95,
        longitude=77.55
    )
    
    # Anonymous request
    res_anon = client.post(f'/api/v1/issues/{issue.id}/upvote')
    assert res_anon.status_code == 401

def test_api_upvote_logged_in(client, sample_category, citizen_user):
    issue = IssueService.create_issue(
        title='Upvotable Issue',
        description='Desc',
        category_id=sample_category.id,
        address='Addr',
        latitude=12.95,
        longitude=77.55
    )
    
    login(client, 'citizen@test.org', 'citizenpass123')
    res = client.post(f'/api/v1/issues/{issue.id}/upvote')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['upvotes_count'] == 1
    assert data['has_upvoted'] is True

def test_api_get_categories(client, sample_category):
    response = client.get('/api/v1/categories')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) >= 1
    assert data[0]['name'] == sample_category.name
