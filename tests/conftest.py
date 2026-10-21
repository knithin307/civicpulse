import pytest
from app import create_app
from app.extensions import db as _db
from app.models.user import User, UserRole
from app.models.department import Department
from app.models.category import Category
from app.models.issue import Issue, IssueStatus, IssuePriority

@pytest.fixture(scope='function')
def app():
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def db_session(app):
    return _db.session

@pytest.fixture
def sample_department(app, db_session):
    dept = Department(
        name='Roads & Infrastructure',
        code='ROADS',
        description='Roadway maintenance',
        contact_email='roads@test.org',
        icon='bi-cone-striped'
    )
    db_session.add(dept)
    db_session.commit()
    return dept

@pytest.fixture
def sample_category(app, db_session, sample_department):
    cat = Category(
        name='Potholes & Broken Asphalt',
        department_id=sample_department.id,
        description='Damaged roads',
        icon='bi-cone-striped',
        default_severity=IssuePriority.HIGH,
        sla_hours=24
    )
    db_session.add(cat)
    db_session.commit()
    return cat

@pytest.fixture
def admin_user(app, db_session):
    admin = User(
        full_name='Test Admin',
        email='admin@test.org',
        role=UserRole.ADMIN
    )
    admin.set_password('adminpass123')
    db_session.add(admin)
    db_session.commit()
    return admin

@pytest.fixture
def officer_user(app, db_session, sample_department):
    officer = User(
        full_name='Test Officer',
        email='officer@test.org',
        role=UserRole.OFFICER,
        department_id=sample_department.id
    )
    officer.set_password('officerpass123')
    db_session.add(officer)
    db_session.commit()
    return officer

@pytest.fixture
def citizen_user(app, db_session):
    citizen = User(
        full_name='Test Citizen',
        email='citizen@test.org',
        role=UserRole.CITIZEN
    )
    citizen.set_password('citizenpass123')
    db_session.add(citizen)
    db_session.commit()
    return citizen

def login(client, email, password):
    return client.post('/auth/login', data={
        'email': email,
        'password': password
    }, follow_redirects=True)

def logout(client):
    return client.get('/auth/logout', follow_redirects=True)
