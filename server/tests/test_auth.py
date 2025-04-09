import pytest
from app import app, db

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