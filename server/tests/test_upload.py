import pytest
import sys
import os
import io
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db, Task, User


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

def register_user(client, email, role, name="Jan"):
    return client.post('/register', json={
        'name': name,
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

UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']

def test_upload_file_success(client):
    with app.app_context():
        register_user(client, "student@test.com", "student")
        student = User.query.filter_by(email="student@test.com").first()

        task = Task(content="Test task", student_id=student.id, teacher_id=1, max_points=10)
        db.session.add(task)
        db.session.commit()

        login_user(client, "student@test.com", "pass123")

        data = {
            'file': (io.BytesIO(b"test content"), 'testfile.txt')
        }

        response = client.post(f'/upload/{task.id}', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        json_data = response.get_json()
        assert "filename" in json_data

        assert os.path.exists(os.path.join(UPLOAD_FOLDER, json_data["filename"]))


def test_upload_file_unauthorized(client):
    with app.app_context():
        register_user(client, "teacher@test.com", "teacher")
        login_user(client, "teacher@test.com", "pass123")

        data = {
            'file': (io.BytesIO(b"test"), 'unauthorized.txt')
        }

        response = client.post('/upload/1', data=data, content_type='multipart/form-data')
        assert response.status_code == 403
        assert b"Unauthorized" in response.data


def test_upload_file_no_file(client):
    with app.app_context():
        register_user(client, "student2@test.com", "student")
        login_user(client, "student2@test.com", "pass123")

        response = client.post('/upload/1', data={}, content_type='multipart/form-data')
        assert response.status_code == 400
        assert b"No file part" in response.data


def test_upload_file_invalid_extension(client):
    with app.app_context():
        register_user(client, "student3@test.com", "student")
        student = User.query.filter_by(email="student3@test.com").first()
        task = Task(content="Test", student_id=student.id, teacher_id=1, max_points=10)
        db.session.add(task)
        db.session.commit()

        login_user(client, "student3@test.com", "pass123")

        data = {
            'file': (io.BytesIO(b"fake"), 'malware.exe')
        }

        response = client.post(f'/upload/{task.id}', data=data, content_type='multipart/form-data')
        assert response.status_code == 400
        assert b"Invalid file type" in response.data


def test_file_download(client):
    with app.app_context():
        test_filename = "download_test.txt"
        file_path = os.path.join(UPLOAD_FOLDER, test_filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        with open(file_path, "w") as f:
            f.write("hello world")

        response = client.get(f'/uploads/{test_filename}')
        assert response.status_code == 200
        assert b"hello world" in response.data
