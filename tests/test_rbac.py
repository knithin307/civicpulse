from tests.conftest import login, logout

def test_anonymous_access_protected_routes(client):
    # Should redirect to login
    res1 = client.get('/citizen/dashboard')
    assert res1.status_code == 302
    assert '/auth/login' in res1.headers['Location']
    
    res2 = client.get('/officer/dashboard')
    assert res2.status_code == 302
    assert '/auth/login' in res2.headers['Location']
    
    res3 = client.get('/admin/dashboard')
    assert res3.status_code == 302
    assert '/auth/login' in res3.headers['Location']

def test_citizen_cannot_access_officer_or_admin_portal(client, citizen_user):
    login(client, 'citizen@test.org', 'citizenpass123')
    
    res_officer = client.get('/officer/dashboard')
    assert res_officer.status_code == 403
    
    res_admin = client.get('/admin/dashboard')
    assert res_admin.status_code == 403

def test_officer_cannot_access_admin_portal(client, officer_user):
    login(client, 'officer@test.org', 'officerpass123')
    
    res_admin = client.get('/admin/dashboard')
    assert res_admin.status_code == 403
    
    res_officer = client.get('/officer/dashboard')
    assert res_officer.status_code == 200

def test_admin_has_full_access(client, admin_user):
    login(client, 'admin@test.org', 'adminpass123')
    
    res_admin = client.get('/admin/dashboard')
    assert res_admin.status_code == 200
    
    res_officer = client.get('/officer/dashboard')
    assert res_officer.status_code == 200
    
    res_citizen = client.get('/citizen/dashboard')
    assert res_citizen.status_code == 200
