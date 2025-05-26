import pytest
from datetime import datetime
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

def login_user(client, email, password="pass123"):
    return client.post('/login', json={
        'email': email,
        'password': password
    })

def create_task(student_id, teacher_id):
    task = Task(
        content="Task 1",
        due_date=datetime.now(),
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
        
        task = Task(
            content="Test task",
            student_id=student.id,
            teacher_id=teacher.id,
            due_date=datetime.now(),
            max_points=10
        )
        db.session.add(task)
        db.session.commit()
        
        response = client.get('/tasks', query_string={
            'user_id': teacher.id,
            'role': 'teacher'
        })
        assert response.status_code == 200
        tasks = response.get_json()
        assert isinstance(tasks, list)
        assert len(tasks) == 1
        assert tasks[0]['student_name'] == "Jan Nowak"
        assert tasks[0]['content'] == "Test task"
        assert tasks[0]['max_points'] == 10

def test_get_tasks_as_student(client):
    with app.app_context():
        register_user(client, "teacher2@test.com", "teacher")
        register_user(client, "student2@test.com", "student")
        
        teacher = User.query.filter_by(email="teacher2@test.com").first()
        student = User.query.filter_by(email="student2@test.com").first()
        
        task = Task(
            content="Student task",
            student_id=student.id,
            teacher_id=teacher.id,
            due_date=datetime.now(),
            max_points=10
        )
        db.session.add(task)
        db.session.commit()
        
        response = client.get('/tasks', query_string={
            'user_id': student.id,
            'role': 'student'
        })
        assert response.status_code == 200
        tasks = response.get_json()
        assert isinstance(tasks, list)
        assert len(tasks) == 1
        assert tasks[0]['teacher_name'] == "Jan Nowak"
        assert tasks[0]['content'] == "Student task"

def test_get_tasks_missing_params(client):
    response = client.get('/tasks')
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["message"] == "Missing user_id or role parameter"

# POST /tasks
def test_create_task_success(client):
    with app.app_context():
        register_user(client, "teacher3@test.com", "teacher")
        register_user(client, "student3@test.com", "student")
        
        teacher = User.query.filter_by(email="teacher3@test.com").first()
        student = User.query.filter_by(email="student3@test.com").first()
        
        task_data = {
            "content": "New task",
            "student_id": student.id,
            "teacher_id": teacher.id,
            "due_date": datetime.now().strftime("%Y-%m-%d"),
            "max_points": 10
        }
        
        response = client.post('/tasks', json=task_data)
        assert response.status_code == 201
        json_data = response.get_json()
        assert json_data["message"] == "Task created successfully"

def test_create_task_invalid_student(client):
    with app.app_context():
        register_user(client, "teacher4@test.com", "teacher")
        teacher = User.query.filter_by(email="teacher4@test.com").first()
        
        task_data = {
            "content": "Invalid task",
            "student_id": 9999,
            "teacher_id": teacher.id,
            "due_date": datetime.now().strftime("%Y-%m-%d"),
            "max_points": 10
        }
        
        response = client.post('/tasks', json=task_data)
        assert response.status_code == 404
        json_data = response.get_json()
        assert json_data["message"] == "Student not found"

# POST /task/complete/<task_id>
def test_complete_task_success(client):
    with app.app_context():
        register_user(client, "teacher5@test.com", "teacher")
        register_user(client, "student5@test.com", "student")
        
        teacher = User.query.filter_by(email="teacher5@test.com").first()
        student = User.query.filter_by(email="student5@test.com").first()
        
        task = Task(
            content="Task to complete",
            student_id=student.id,
            teacher_id=teacher.id,
            due_date=datetime.now(),
            max_points=10
        )
        db.session.add(task)
        db.session.commit()
        
        completion_data = {
            "student_id": student.id,
            "answer": "This is my answer"
        }
        
        response = client.post(f'/task/complete/{task.id}', json=completion_data)
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data["message"] == "Task marked as completed"
        
        updated_task = Task.query.get(task.id)
        assert updated_task.completed is True
        assert updated_task.answer == "This is my answer"
        assert updated_task.sent_date is not None

def test_complete_task_unauthorized(client):
    with app.app_context():
        register_user(client, "teacher6@test.com", "teacher")
        register_user(client, "student6@test.com", "student")
        register_user(client, "other@test.com", "student")
        
        teacher = User.query.filter_by(email="teacher6@test.com").first()
        student = User.query.filter_by(email="student6@test.com").first()
        
        task = Task(
            content="Unauthorized task",
            student_id=student.id,
            teacher_id=teacher.id,
            due_date=datetime.now(),
            max_points=10
        )
        db.session.add(task)
        db.session.commit()
        
        other_student = User.query.filter_by(email="other@test.com").first()
        completion_data = {
            "student_id": other_student.id,
            "answer": "Unauthorized answer"
        }
        
        response = client.post(f'/task/complete/{task.id}', json=completion_data)
        assert response.status_code == 403
        json_data = response.get_json()
        assert json_data["message"] == "Unauthorized or task not found"

# POST /task/grade/<task_id>
def test_grade_task_success(client):
    with app.app_context():
        register_user(client, "teacher7@test.com", "teacher")
        register_user(client, "student7@test.com", "student")
        
        teacher = User.query.filter_by(email="teacher7@test.com").first()
        student = User.query.filter_by(email="student7@test.com").first()
        
        task = Task(
            content="Task to grade",
            student_id=student.id,
            teacher_id=teacher.id,
            due_date=datetime.now(),
            max_points=10,
            completed=True,
            answer="Student's answer"
        )
        db.session.add(task)
        db.session.commit()
        
        grade_data = {
            "teacher_id": teacher.id,
            "grade": 8,
            "comment": "Good work!"
        }
        
        response = client.post(f'/task/grade/{task.id}', json=grade_data)
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data["message"] == "Task graded successfully"
        
        graded_task = Task.query.get(task.id)
        assert graded_task.grade == 8
        assert graded_task.comment == "Good work!"

def test_grade_task_invalid_grade(client):
    with app.app_context():
        register_user(client, "teacher8@test.com", "teacher")
        register_user(client, "student8@test.com", "student")
        
        teacher = User.query.filter_by(email="teacher8@test.com").first()
        student = User.query.filter_by(email="student8@test.com").first()
        
        task = Task(
            content="Invalid grade task",
            student_id=student.id,
            teacher_id=teacher.id,
            due_date=datetime.now(),
            max_points=10,
            completed=True,
            answer="Student's answer"
        )
        db.session.add(task)
        db.session.commit()
        
        grade_data = {
            "teacher_id": teacher.id,
            "grade": 11,
            "comment": "Invalid grade"
        }
        
        response = client.post(f'/task/grade/{task.id}', json=grade_data)
        assert response.status_code == 400
        json_data = response.get_json()
        assert json_data["message"] == "Invalid action"

def test_get_task_details(client):
    with app.app_context():
        register_user(client, "teacher9@test.com", "teacher")
        register_user(client, "student9@test.com", "student")
        
        teacher = User.query.filter_by(email="teacher9@test.com").first()
        student = User.query.filter_by(email="student9@test.com").first()
        
        task = Task(
            content="Detailed task",
            student_id=student.id,
            teacher_id=teacher.id,
            due_date=datetime.now(),
            max_points=10,
            completed=True,
            answer="Detailed answer",
            grade=9,
            comment="Excellent work"
        )
        db.session.add(task)
        db.session.commit()
        
        response = client.get(f'/task/{task.id}', query_string={
            'user_id': teacher.id,
            'role': 'teacher'
        })
        assert response.status_code == 200
        task_data = response.get_json()
        assert task_data['content'] == "Detailed task"
        assert task_data['grade'] == 9
        assert task_data['comment'] == "Excellent work"
        
        response = client.get(f'/task/{task.id}', query_string={
            'user_id': student.id,
            'role': 'student'
        })
        assert response.status_code == 200
        task_data = response.get_json()
        assert task_data['content'] == "Detailed task"
        assert task_data['grade'] == 9
        assert task_data['comment'] == "Excellent work"