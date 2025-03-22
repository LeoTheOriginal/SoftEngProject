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

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        login_user(user)
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
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout successful"}), 200

@app.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    if current_user.role == 'teacher':
        tasks = Task.query.filter_by(teacher_id=current_user.id).all()
    else:
        tasks = Task.query.filter_by(student_id=current_user.id).all()

    task_list = [{
        "id": task.id,
        "content": task.content,
        "due_date": task.due_date.strftime("%Y-%m-%d") if task.due_date else None,
        "completed": task.completed,
        "max_points": task.max_points,
        "grade": task.grade
    } for task in tasks]

    return jsonify(task_list)

@app.route('/tasks', methods=['POST'])
@login_required
def create_task():
    if current_user.role != 'teacher':
        return jsonify({"message": "Unauthorized"}), 403

    data = request.json
    new_task = Task(
        content=data['content'],
        student_id=data['student_id'],
        teacher_id=current_user.id,
        due_date=datetime.strptime(data['due_date'], "%Y-%m-%d"),
        max_points=data['max_points']
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"message": "Task created successfully"}), 201

@app.route('/task/complete/<int:task_id>', methods=['POST'])
@login_required
def mark_task_completed(task_id):
    task = Task.query.get(task_id)
    if not task or task.student_id != current_user.id:
        return jsonify({"message": "Unauthorized"}), 403

    data = request.json
    task.answer = data.get('answer', None)
    task.sent_date = datetime.now()
    task.completed = True

    db.session.commit()
    return jsonify({"message": "Task marked as completed"}), 200

@app.route('/task/grade/<int:task_id>', methods=['POST'])
@login_required
def grade_task(task_id):
    task = Task.query.get(task_id)
    if not task or task.teacher_id != current_user.id:
        return jsonify({"message": "Unauthorized"}), 403

    data = request.json
    grade = data.get('grade')
    if grade and 0 < int(grade) <= task.max_points:
        task.grade = int(grade)
        db.session.commit()
        return jsonify({"message": "Task graded successfully"}), 200

    return jsonify({"message": "Invalid grade"}), 400

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return jsonify({"message": "File uploaded", "filename": filename}), 200

    return jsonify({"message": "Invalid file type"}), 400

@app.route('/uploads/<path:filepath>')
def uploaded_file(filepath):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filepath, as_attachment=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run(debug=True)