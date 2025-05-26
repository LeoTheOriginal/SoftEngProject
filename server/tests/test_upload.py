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

def login_user(client, email, password="pass123"):
    return client.post('/login', json={
        'email': email,
        'password': password
    })

UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']

def test_upload_file_success(client):
    with app.app_context():
        register_user(client, "teacher1@test.com", "teacher")
        register_user(client, "student1@test.com", "student")
        
        teacher = User.query.filter_by(email="teacher1@test.com").first()
        student = User.query.filter_by(email="student1@test.com").first()
        
        task = Task(
            content="Upload test task",
            student_id=student.id,
            teacher_id=teacher.id,
            max_points=10
        )
        db.session.add(task)
        db.session.commit()
        
        data = {
            'file': (io.BytesIO(b"test content"), 'test.txt'),
            'student_id': student.id
        }
        
        response = client.post(f'/upload/{task.id}', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        json_data = response.get_json()
        assert "filename" in json_data
        assert os.path.exists(os.path.join(UPLOAD_FOLDER, json_data["filename"]))
        
        updated_task = Task.query.get(task.id)
        assert updated_task.file_path == os.path.join(UPLOAD_FOLDER, json_data["filename"])

def test_upload_file_no_student_id(client):
    with app.app_context():
        register_user(client, "teacher2@test.com", "teacher")
        register_user(client, "student2@test.com", "student")
        
        teacher = User.query.filter_by(email="teacher2@test.com").first()
        student = User.query.filter_by(email="student2@test.com").first()
        
        task = Task(
            content="Upload test task",
            student_id=student.id,
            teacher_id=teacher.id,
            max_points=10
        )
        db.session.add(task)
        db.session.commit()
        
        data = {
            'file': (io.BytesIO(b"test content"), 'test.txt')
        }
        
        response = client.post(f'/upload/{task.id}', data=data, content_type='multipart/form-data')
        assert response.status_code == 400
        json_data = response.get_json()
        assert json_data["message"] == "Missing student_id parameter"

def test_upload_file_wrong_student(client):
    with app.app_context():
        register_user(client, "teacher3@test.com", "teacher")
        register_user(client, "student3@test.com", "student")
        register_user(client, "other@test.com", "student")
        
        teacher = User.query.filter_by(email="teacher3@test.com").first()
        student = User.query.filter_by(email="student3@test.com").first()
        other_student = User.query.filter_by(email="other@test.com").first()
        
        task = Task(
            content="Upload test task",
            student_id=student.id,
            teacher_id=teacher.id,
            max_points=10
        )
        db.session.add(task)
        db.session.commit()
        
        data = {
            'file': (io.BytesIO(b"test content"), 'test.txt'),
            'student_id': other_student.id
        }
        
        response = client.post(f'/upload/{task.id}', data=data, content_type='multipart/form-data')
        assert response.status_code == 404
        json_data = response.get_json()
        assert json_data["message"] == "Task not found or not assigned to you"

def test_upload_file_no_file(client):
    with app.app_context():
        register_user(client, "teacher4@test.com", "teacher")
        register_user(client, "student4@test.com", "student")
        
        teacher = User.query.filter_by(email="teacher4@test.com").first()
        student = User.query.filter_by(email="student4@test.com").first()
        
        task = Task(
            content="Upload test task",
            student_id=student.id,
            teacher_id=teacher.id,
            max_points=10
        )
        db.session.add(task)
        db.session.commit()
        
        data = {
            'student_id': student.id
        }
        
        response = client.post(f'/upload/{task.id}', data=data, content_type='multipart/form-data')
        assert response.status_code == 400
        json_data = response.get_json()
        assert json_data["message"] == "No file part"

def test_upload_file_invalid_extension(client):
    with app.app_context():
        register_user(client, "teacher5@test.com", "teacher")
        register_user(client, "student5@test.com", "student")
        
        teacher = User.query.filter_by(email="teacher5@test.com").first()
        student = User.query.filter_by(email="student5@test.com").first()
        
        task = Task(
            content="Upload test task",
            student_id=student.id,
            teacher_id=teacher.id,
            max_points=10
        )
        db.session.add(task)
        db.session.commit()
        
        data = {
            'file': (io.BytesIO(b"test content"), 'test.exe'),
            'student_id': student.id
        }
        
        response = client.post(f'/upload/{task.id}', data=data, content_type='multipart/form-data')
        assert response.status_code == 400
        json_data = response.get_json()
        assert json_data["message"] == "Invalid file type"

def test_file_download(client):
    with app.app_context():
        test_filename = "test_download.txt"
        file_path = os.path.join(UPLOAD_FOLDER, test_filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        test_content = "Hello, this is a test file!"
        with open(file_path, "w") as f:
            f.write(test_content)
        
        try:
            response = client.get(f'/uploads/{test_filename}')
            assert response.status_code == 200
            assert response.data.decode() == test_content
        finally:
            for _ in range(3):
                try:
                    if os.path.exists(file_path):
                        os.close(os.open(file_path, os.O_RDONLY))
                        os.remove(file_path)
                    break
                except (OSError, PermissionError):
                    import time
                    time.sleep(0.1)

def test_file_download_not_found(client):
    response = client.get('/uploads/nonexistent.txt')
    assert response.status_code == 404
