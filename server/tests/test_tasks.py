import pytest
from datetime import date
import sys
import os
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

def create_task(student_id, teacher_id):
    task = Task(
        content="Task 1",
        due_date=date.today(),
        answer=None,
        completed=False,
        max_points=10,
        grade=None,
        file_path=None,
        student_id=student_id,
        teacher_id=teacher_id
    )
    db.session.add(task)
    db.session.commit()
    return task

# GET /tasks
def test_get_tasks_as_teacher(client):
    with app.app_context():
        register_user(client, "teacher1@test.com", "teacher")
        register_user(client, "student1@test.com", "student")

        teacher = User.query.filter_by(email="teacher1@test.com").first()
        student = User.query.filter_by(email="student1@test.com").first()

        create_task(student_id=student.id, teacher_id=teacher.id)

        login_user(client, "teacher1@test.com", "pass123")
        response = client.get('/tasks')
        assert response.status_code == 200
        tasks = response.get_json()
        print(tasks)
        assert isinstance(tasks, list)
        assert len(tasks) == 1
        assert tasks[0]['student_name'] == "Jan Nowak"

def test_get_tasks_as_student(client):
    with app.app_context():
        register_user(client, "teacher2@test.com", "teacher")
        register_user(client, "student2@test.com", "student")

        teacher = User.query.filter_by(email="teacher2@test.com").first()
        student = User.query.filter_by(email="student2@test.com").first()

        create_task(student_id=student.id, teacher_id=teacher.id)

        login_user(client, "student2@test.com", "pass123")
        response = client.get('/tasks')
        assert response.status_code == 200
        tasks = response.get_json()
        assert isinstance(tasks, list)
        assert len(tasks) == 1
        assert tasks[0]['teacher_name'] == "Jan Nowak"

def test_get_tasks_unauthenticated(client):
    response = client.get('/tasks')
    assert response.status_code == 401


# POST /tasks
def test_create_task_success(client):
    with app.app_context():
        register_user(client, "teacher1@test.com", "teacher")
        register_user(client, "student1@test.com", "student")

        student = User.query.filter_by(email="student1@test.com").first()

        login_user(client, "teacher1@test.com", "pass123")

        task_data = {
            "content": "Task 1",
            "student_id": student.id,
            "due_date": date.today().strftime("%Y-%m-%d"),
            "max_points": 10
        }

        response = client.post('/tasks', json=task_data)
        assert response.status_code == 201
        assert b"Task created successfully" in response.data

def test_create_task_unauthorized_user(client):
    with app.app_context():
        register_user(client, "student2@test.com", "student")
        login_user(client, "student2@test.com", "pass123")

        task_data = {
            "content": "Task 0",
            "student_id": 1,
            "due_date": date.today().strftime("%Y-%m-%d"),
            "max_points": 10
        }

        response = client.post('/tasks', json=task_data)
        assert response.status_code == 403
        assert b"Unauthorized" in response.data

def test_create_task_student_not_found(client):
    with app.app_context():
        register_user(client, "teacher2@test.com", "teacher")
        login_user(client, "teacher2@test.com", "pass123")

        task_data = {
            "content": "Task 1",
            "student_id": 999, 
            "due_date": date.today().strftime("%Y-%m-%d"),
            "max_points": 10
        }

        response = client.post('/tasks', json=task_data)
        assert response.status_code == 404
        assert b"Student not found" in response.data

# POST /task/complete/<task_id>
def test_mark_task_completed_success(client):
    with app.app_context():
        register_user(client, "teacher1@test.com", "teacher")
        register_user(client, "student1@test.com", "student")

        teacher = User.query.filter_by(email="teacher1@test.com").first()
        student = User.query.filter_by(email="student1@test.com").first()

        task = create_task(student_id=student.id, teacher_id=teacher.id)

        login_user(client, "student1@test.com", "pass123")

        task_data = {
            "answer": "Task 1 answer"
        }

        response = client.post(f'/task/complete/{task.id}', json=task_data)
        assert response.status_code == 200
        assert b"Task marked as completed" in response.data

        task = Task.query.get(task.id)
        assert task.completed is True
        assert task.answer == "Task 1 answer"

def test_mark_task_completed_unauthorized_user(client):
    with app.app_context():
        register_user(client, "teacher2@test.com", "teacher")
        register_user(client, "student2@test.com", "student")
        register_user(client, "student0@test.com", "student")

        teacher = User.query.filter_by(email="teacher2@test.com").first()
        student = User.query.filter_by(email="student2@test.com").first()

        task = create_task(student_id=student.id, teacher_id=teacher.id)

        login_user(client, "student0@test.com", "pass123")

        task_data = {
            "answer": "Task answer"
        }

        response = client.post(f'/task/complete/{task.id}', json=task_data)
        assert response.status_code == 403
        assert b"Unauthorized" in response.data

def test_mark_task_completed_missing_answer(client):
    with app.app_context():
        register_user(client, "teacher3@test.com", "teacher")
        register_user(client, "student3@test.com", "student")

        teacher = User.query.filter_by(email="teacher3@test.com").first()
        student = User.query.filter_by(email="student3@test.com").first()

        task = create_task(student_id=student.id, teacher_id=teacher.id)

        login_user(client, "student3@test.com", "pass123")

        task_data = {}

        response = client.post(f'/task/complete/{task.id}', json=task_data)
        assert response.status_code == 400
        assert b"Answer is required" in response.data

def test_mark_task_completed_task_not_found(client):
    with app.app_context():
        register_user(client, "teacher4@test.com", "teacher")
        register_user(client, "student4@test.com", "student")

        teacher = User.query.filter_by(email="teacher4@test.com").first()
        student = User.query.filter_by(email="student4@test.com").first()

        login_user(client, "student4@test.com", "pass123")

        task_data = {
            "answer": "Task answer"
        }

        response = client.post('/task/complete/9999', json=task_data)
        assert response.status_code == 403
        assert b"Unauthorized" in response.data


# POST /task/grade/<task_id>
def test_grade_task_success(client):
    with app.app_context():
        register_user(client, "teacher5@test.com", "teacher")
        register_user(client, "student5@test.com", "student")

        teacher = User.query.filter_by(email="teacher5@test.com").first()
        student = User.query.filter_by(email="student5@test.com").first()

        # Tworzenie zadania
        task = create_task(student_id=student.id, teacher_id=teacher.id)

        task.answer = "Task answer"
        task.completed = True
        db.session.commit()

        login_user(client, "teacher5@test.com", "pass123")

        # Ocena zadania
        task_data = {
            "grade": 8
        }

        response = client.post(f'/task/grade/{task.id}', json=task_data)
        assert response.status_code == 200
        assert b"Task graded successfully" in response.data

        task = Task.query.get(task.id)
        assert task.grade == 8

def test_grade_task_student_access(client):
    with app.app_context():
        register_user(client, "teacher6@test.com", "teacher")
        register_user(client, "student6@test.com", "student")

        teacher = User.query.filter_by(email="teacher6@test.com").first()
        student = User.query.filter_by(email="student6@test.com").first()

        task = create_task(student_id=student.id, teacher_id=teacher.id)

        task.answer = "Task answer"
        task.completed = True
        db.session.commit()

        login_user(client, "student6@test.com", "pass123")

        task_data = {
            "grade": 8
        }

        response = client.post(f'/task/grade/{task.id}', json=task_data)
        assert response.status_code == 403
        assert b"Unauthorized" in response.data

def test_grade_task_task_not_found(client):
    with app.app_context():
        register_user(client, "teacher7@test.com", "teacher")
        register_user(client, "student7@test.com", "student")

        teacher = User.query.filter_by(email="teacher7@test.com").first()
        student = User.query.filter_by(email="student7@test.com").first()

        login_user(client, "teacher7@test.com", "pass123")

        task_data = {
            "grade": 9
        }

        response = client.post('/task/grade/9999', json=task_data)
        assert response.status_code == 403
        assert b"Unauthorized" in response.data