import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, User, Log

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        db.session.remove()
        db.drop_all()

def register_user(client, email, role):
    return client.post('/register', json={
        'name': "Jan",
        'surname': "Nowak",
        'email': email,
        'password': "pass123",
        'role': role
    })

def login_user(client, email, password):
    return client.post('/login', json={
        'email': email,
        'password': password
    })

def test_register_student(client):
    response = register_user(client, "student1@test.com", "student")
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data["message"] == "User registered successfully"

def test_register_teacher(client):
    response = register_user(client, "teacher1@test.com", "teacher")
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data["message"] == "User registered successfully"

def test_login_student(client):
    register_user(client, "student2@test.com", "student")
    response = login_user(client, "student2@test.com", "pass123")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["message"] == "Login successful"
    assert json_data["user"]["role"] == "student"

def test_login_teacher(client):
    register_user(client, "teacher2@test.com", "teacher")
    response = login_user(client, "teacher2@test.com", "pass123")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["message"] == "Login successful"
    assert json_data["user"]["role"] == "teacher"

def test_login_invalid_pass(client):
    register_user(client, "student3@test.com", "student")
    response = login_user(client, "student3@test.com", "wrongpass")
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data["message"] == "Invalid credentials"

def test_login_no_user(client):
    response = login_user(client, "nonexistent@test.com", "pass123")
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data["message"] == "Invalid credentials"

def test_register_duplicate_email(client):
    register_user(client, "student5@test.com", "student")
    response = register_user(client, "student5@test.com", "student")
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["message"] == "Email already in use"

def test_register_duplicate_email_different_roles(client):
    register_user(client, "user1@test.com", "student")
    response = register_user(client, "user1@test.com", "teacher")
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["message"] == "Email already in use"

def test_get_students(client):
    register_user(client, "teacher1@test.com", "teacher")
    register_user(client, "student6@test.com", "student")
    response = client.get('/students')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    student = next((s for s in data if s["name"] == "Jan Nowak"), None)
    assert student is not None
    assert "id" in student

def test_logout(client):
    register_user(client, "student7@test.com", "student")
    login_user(client, "student7@test.com", "pass123")
    response = client.post('/logout')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["message"] == "Logout successful"

def test_get_logs_as_admin(client):
    with app.app_context():
        register_user(client, "admin1@test.com", "admin")
        admin = User.query.filter_by(email="admin1@test.com").first()
        response = client.get("/logs", query_string={"admin_id": admin.id})
        assert response.status_code == 200
        logs = response.get_json()
        assert isinstance(logs, list)
        assert len(logs) > 0
        assert all("action" in log and log["action"] for log in logs)

def test_get_logs_missing_admin_param(client):
    response = client.get("/logs")
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["message"] == "Missing admin_id parameter"

def test_get_logs_as_non_admin(client):
    with app.app_context():
        register_user(client, "student8@test.com", "student")
        student = User.query.filter_by(email="student8@test.com").first()
        response = client.get("/logs", query_string={"admin_id": student.id})
        assert response.status_code == 403
        json_data = response.get_json()
        assert json_data["message"] == "Unauthorized"

def test_logs_format(client):
    with app.app_context():
        register_user(client, "admin2@test.com", "admin")
        admin = User.query.filter_by(email="admin2@test.com").first()
        response = client.get("/logs", query_string={"admin_id": admin.id})
        assert response.status_code == 200
        logs = response.get_json()
        assert len(logs) > 0
        log = logs[0]
        assert all(key in log for key in ["id", "user", "action", "timestamp"])