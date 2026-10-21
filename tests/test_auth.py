from tests.conftest import login, logout
from app.models.user import User

def test_register_new_citizen(client, db_session):
    response = client.post('/auth/register', data={
        'full_name': 'New Resident',
        'email': 'newresident@example.com',
        'phone': '555-0199',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    user = User.query.filter_by(email='newresident@example.com').first()
    assert user is not None
    assert user.full_name == 'New Resident'
    assert user.role == 'citizen'
    assert user.check_password('password123')

def test_register_password_mismatch(client):
    response = client.post('/auth/register', data={
        'full_name': 'Mismatch User',
        'email': 'mismatch@example.com',
        'password': 'password123',
        'confirm_password': 'differentpassword'
    }, follow_redirects=True)
    
    assert b'Passwords do not match' in response.data
    user = User.query.filter_by(email='mismatch@example.com').first()
    assert user is None

def test_login_successful(client, citizen_user):
    response = login(client, 'citizen@test.org', 'citizenpass123')
    assert response.status_code == 200
    assert b'Welcome back, Test Citizen!' in response.data

def test_login_invalid_password(client, citizen_user):
    response = login(client, 'citizen@test.org', 'wrongpassword')
    assert response.status_code == 200
    assert b'Invalid email address or password' in response.data

def test_logout(client, citizen_user):
    login(client, 'citizen@test.org', 'citizenpass123')
    response = logout(client)
    assert response.status_code == 200
    assert b'You have been signed out safely.' in response.data

def test_profile_update(client, citizen_user):
    login(client, 'citizen@test.org', 'citizenpass123')
    response = client.post('/auth/profile', data={
        'full_name': 'Updated Citizen Name',
        'phone': '555-999-8888'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Profile updated successfully.' in response.data
    assert citizen_user.full_name == 'Updated Citizen Name'
    assert citizen_user.phone == '555-999-8888'
