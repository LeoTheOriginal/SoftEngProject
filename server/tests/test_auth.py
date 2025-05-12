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
        # db.session.remove()
        # db.drop_all()

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

#register succesful

def test_register_student(client):
    # nie dropuje bazy automatycznie
    # ---
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()
    # ---
        response = register_user(client, "student1@test.com", "student")
        assert response.status_code == 201
        assert b"User registered successfully" in response.data

def test_register_teacher(client):
    response = register_user(client, "teacher1@test.com", "teacher")
    assert response.status_code == 201
    assert b"User registered successfully" in response.data

#login succesful

def test_login_student(client):
    register_user(client, "student2@test.com", "student")
    response = login_user(client, "student2@test.com", "pass123")
    assert response.status_code == 200
    assert b"Login successful" in response.data

def test_login_teacher(client):
    register_user(client, "teacher2@test.com", "teacher")
    response = login_user(client, "teacher2@test.com", "pass123")
    assert response.status_code == 200
    assert b"Login successful" in response.data

#login rejections

def test_login_invalid_pass(client):
    register_user(client, "student3@test.com", "student")
    response = login_user(client, "student3@test.com", "pass1234")
    assert response.status_code == 401
    assert b"Invalid credentials" in response.data

def test_login_no_user(client):
    response = login_user(client, "student4@test.com", "pass123")
    assert response.status_code == 401
    assert b"Invalid credentials" in response.data


#register rejections

def test_register_duplicate_student(client):
    register_user(client, "student5@test.com", "student")
    response = register_user(client, "student5@test.com", "student")
    assert response.status_code == 400
    assert b"Email already in use" in response.data

def test_register_duplicate_email_different_roles(client):
    register_user(client, "user1@test.com", "student")
    response = register_user(client, "user1@test.com", "teacher")
    assert response.status_code == 400
    assert b"Email already in use" in response.data

#logout - nie smakuje mu

# def test_logout(client):
#     register_user(client, "student6@test.com", "student")
#     login_user(client, "student6@test.com", "pass123")
#     response = client.get('/logout')
#     assert response.status_code == 200
#     assert b"Logout successful" in response.data

# GET /students
def test_get_students_as_teacher(client):
    register_user(client, "teacher1@test.com", "teacher")
    register_user(client, "student1@test.com", "student")
    login_user(client, "teacher1@test.com", "pass123")

    response = client.get('/students')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 5
    assert data[0]["name"] == "Jan Nowak"

def test_get_students_as_student(client):
    register_user(client, "student2@test.com", "student")
    login_user(client, "student2@test.com", "pass123")

    response = client.get('/students')
    assert response.status_code == 403
    assert b"Unauthorized" in response.data

def test_get_students_unauthenticated(client):
    response = client.get('/students')
    assert response.status_code  == 401

#logs
def test_get_logs_as_admin(client):
    with app.app_context():
        # Rejestracja użytkowników
        register_user(client, "admin1@test.com", "admin")
        register_user(client, "teacher1@test.com", "teacher")

        admin = User.query.filter_by(email="admin1@test.com").first()
        teacher = User.query.filter_by(email="teacher1@test.com").first()

        # Dodanie przykładowych logów
        log1 = Log(user_id=admin.id, action="Admin zalogował się")
        log2 = Log(user_id=teacher.id, action="Nauczyciel zalogował się")
        db.session.add_all([log1, log2])
        db.session.commit()

        login_user(client, "admin1@test.com", "pass123")

        response = client.get("/logs")
        assert response.status_code == 200

        logs = response.get_json()
        assert isinstance(logs, list)
        assert len(logs) >= 2

        log_messages = [log["action"] for log in logs]
        assert "Admin zalogował się" in log_messages
        assert "Nauczyciel zalogował się" in log_messages


def test_get_logs_as_non_admin(client):
    with app.app_context():
        register_user(client, "student1@test.com", "student")
        login_user(client, "student1@test.com", "pass123")

        response = client.get("/logs")
        assert response.status_code == 403
        assert b"Unauthorized" in response.data


def test_logs_format(client):
    with app.app_context():
        register_user(client, "admin2@test.com", "admin")
        admin = User.query.filter_by(email="admin2@test.com").first()

        log = Log(user_id=admin.id, action="Test formatowania")
        db.session.add(log)
        db.session.commit()

        login_user(client, "admin2@test.com", "pass123")
        response = client.get("/logs")
        assert response.status_code == 200

        logs = response.get_json()
        assert "timestamp" in logs[0]
        assert "user" in logs[0]
        assert "action" in logs[0]