from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import uuid

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///changeItXD.db'
app.config['SECRET_KEY'] = 'trzebazmienic'
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.DateTime, nullable=True)
    sent_date = db.Column(db.DateTime, nullable=True)
    answer = db.Column(db.String(200), nullable=True)
    max_points = db.Column(db.Integer, nullable=True)
    grade = db.Column(db.Integer, nullable=True)
    comment = db.Column(db.String(200), nullable=True)
    file_path = db.Column(db.String(255), nullable=True)

    student = db.relationship('User', foreign_keys=[student_id], backref='tasks')
    teacher = db.relationship('User', foreign_keys=[teacher_id])

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Może być None dla ogólnych logów
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='logs')

def log_action(user_id, action):
    user = User.query.get(user_id)
    new_log = Log(user_id=user_id, action=f"{user.name} {user.surname}, " + action)
    db.session.add(new_log)
    db.session.commit()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        login_user(user)
        log_action(user.id, "Logged in")
        return jsonify({"message": "Login successful", "user": {"id": user.id, "name": user.name, "role": user.role}})
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"message": "Email already in use"}), 400

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(
        name=data['name'],
        surname=data['surname'],
        email=data['email'],
        password=hashed_password,
        role=data['role']
    )
    db.session.add(new_user)
    db.session.commit()
    log_action(new_user.id, "Registered")
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/logout')
@login_required
def logout():
    logout_user()
    log_action(current_user.id, "Logged out")
    return jsonify({"message": "Logout successful"}), 200

@app.route('/students', methods=['GET'])
@login_required
def get_students():
    if current_user.role != 'teacher':
        log_action(current_user.id, "Unauthorized access to students list")
        return jsonify({"message": "Unauthorized"}), 403

    students = User.query.filter_by(role='student').all()
    student_list = [{"id": student.id, "name": f"{student.name} {student.surname}"} for student in students]
    log_action(current_user.id, "Fetched students list")
    return jsonify(student_list)

@app.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    task_list = []
    if current_user.role == 'teacher':
        tasks = Task.query.filter_by(teacher_id=current_user.id).all()
        task_list = [{
        "id": task.id,
        "content": task.content,
        "due_date": task.due_date.strftime("%Y-%m-%d") if task.due_date else None,
        "answer": task.answer if task.answer else None,
        "completed": task.completed,
        "max_points": task.max_points,
        "grade": task.grade,
        "file_path": task.file_path if task.file_path else None,
        "student_name": f"{task.student.name} {task.student.surname}"
    } for task in tasks]
        log_action(current_user.id, "Fetched tasks list as teacher")
    elif current_user.role == 'student':
        tasks = Task.query.filter_by(student_id=current_user.id).all()
        task_list = [{
        "id": task.id,
        "content": task.content,
        "due_date": task.due_date.strftime("%Y-%m-%d") if task.due_date else None,
        "answer": task.answer if task.answer else None,
        "completed": task.completed,
        "max_points": task.max_points,
        "grade": task.grade,
        "file_path": task.file_path if task.file_path else None,
        "teacher_name": f"{task.teacher.name} {task.teacher.surname}"
    } for task in tasks]
        log_action(current_user.id, "Fetched tasks list as student")
    else:
        log_action(current_user.id, "Unauthorized access to tasks list")
        return jsonify({"message": "Unauthorized"}), 403

    return jsonify(task_list)

@app.route('/tasks', methods=['POST'])
@login_required
def create_task():
    if current_user.role != 'teacher':
        log_action(current_user.id, "Unauthorized task creation attempt")
        return jsonify({"message": "Unauthorized"}), 403

    data = request.json

    student = User.query.filter_by(id=data['student_id'], role='student').first()
    if not student:
        log_action(current_user.id, "Task creation failed - student not found")
        return jsonify({"message": "Student not found"}), 404

    new_task = Task(
        content=data['content'],
        student_id=data['student_id'],
        teacher_id=current_user.id,
        due_date=datetime.strptime(data['due_date'], "%Y-%m-%d"),
        max_points=data['max_points']
    )
    db.session.add(new_task)
    db.session.commit()
    log_action(current_user.id, f"Created task - task_id = {new_task.id} for student {student.name} {student.surname}")
    return jsonify({"message": "Task created successfully"}), 201

@app.route('/task/complete/<int:task_id>', methods=['POST'])
@login_required
def mark_task_completed(task_id):
    task = Task.query.get(task_id)
    if not task or task.student_id != current_user.id:
        log_action(current_user.id, "Unauthorized task completion attempt")
        return jsonify({"message": "Unauthorized"}), 403

    data = request.json
    if not data.get('answer'):
        log_action(current_user.id, "Task completion failed - answer not provided")
        return jsonify({"message": "Answer is required"}), 400
    task.answer = data.get('answer', None)
    task.sent_date = datetime.now()
    task.completed = True

    db.session.commit()
    log_action(current_user.id, f"Task marked as completed - task_id = {task.id}")
    return jsonify({"message": "Task marked as completed"}), 200

@app.route('/task/grade/<int:task_id>', methods=['POST'])
@login_required
def grade_task(task_id):
    task = Task.query.get(task_id)
    if not task or task.teacher_id != current_user.id:
        log_action(current_user.id, "Unauthorized task grading attempt")
        return jsonify({"message": "Unauthorized"}), 403

    data = request.json
    grade = data.get('grade')
    comment = data.get('comment')
    if grade and 0 < int(grade) <= task.max_points and task.completed:
        task.grade = int(grade)
        task.comment = comment if comment else None
        db.session.commit()
        log_action(current_user.id, f"Task graded - task_id = {task.id}, grade = {task.grade}")
        return jsonify({"message": "Task graded successfully"}), 200

    log_action(current_user.id, "Task grading failed - invalid grade or task not completed")
    return jsonify({"message": "Invalid action"}), 400

@app.route('/logs', methods=['GET'])
@login_required
def get_logs():
    if current_user.role != 'admin':
        log_action(current_user.id, "Unauthorized access to logs")
        return jsonify({"message": "Unauthorized"}), 403

    logs = Log.query.order_by(Log.timestamp.desc()).all()
    log_list = [{
        "id": log.id,
        "user": f"{log.user.name} {log.user.surname}" if log.user else "System",
        "action": log.action,
        "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    } for log in logs]

    log_action(current_user.id, "Fetched logs list")
    return jsonify(log_list)

@app.route('/upload/<int:task_id>', methods=['POST'])
def upload_file(task_id):
    if current_user.role != 'student':
        log_action(current_user.id, "Unauthorized file upload attempt")
        return jsonify({"message": "Unauthorized"}), 403
    
    if 'file' not in request.files:
        log_action(current_user.id, "File upload failed - no file part")
        return jsonify({"message": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        log_action(current_user.id, "File upload failed - no selected file")
        return jsonify({"message": "No selected file"}), 400

    task = Task.query.filter_by(id=task_id, student_id=current_user.id).first()
    if not task:
        log_action(current_user.id, "File upload failed - task not found or not assigned to user")
        return jsonify({"message": "Task not found or not assigned to you"}), 404

    if file and allowed_file(file.filename):
        filename = secure_filename(f"{task_id}_{current_user.id}_{file.filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        file.save(file_path)

        task.file_path = file_path
        db.session.commit()
        log_action(current_user.id, f"File uploaded for task_id = {task.id}, filename = {filename}")
        return jsonify({"message": "File uploaded", "filename": filename}), 200

    log_action(current_user.id, "File upload failed - invalid file type")
    return jsonify({"message": "Invalid file type"}), 400

@app.route('/uploads/<path:filepath>')
def uploaded_file(filepath):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filepath, as_attachment=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run(debug=True)