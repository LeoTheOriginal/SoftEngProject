from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os
import uuid

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg'}

app = Flask(__name__)
CORS(app, resources={r"/*": {
    "origins": ["http://localhost:3000", "http://127.0.0.1:3000"], 
    "supports_credentials": True, 
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], 
    "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"]
}})
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

@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def options_handler(path):
    return jsonify({}), 200

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

@app.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({"message": "Logout successful"}), 200

@app.route('/students', methods=['GET'])
def get_students():
    students = User.query.filter_by(role='student').all()
    student_list = [{"id": student.id, "name": f"{student.name} {student.surname}"} for student in students]
    return jsonify(student_list)

@app.route('/tasks', methods=['GET'])
def get_tasks():
    user_id = request.args.get('user_id')
    role = request.args.get('role')
    task_list = []
    
    if not user_id or not role:
        return jsonify({"message": "Missing user_id or role parameter"}), 400
        
    if role == 'teacher':
        tasks = Task.query.filter_by(teacher_id=user_id).all()
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
    elif role == 'student':
        tasks = Task.query.filter_by(student_id=user_id).all()
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
    else:
        return jsonify({"message": "Invalid role"}), 400

    return jsonify(task_list)

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.json
    teacher_id = data.get('teacher_id')
    
    if not teacher_id:
        return jsonify({"message": "Missing teacher_id parameter"}), 400

    teacher = User.query.filter_by(id=teacher_id, role='teacher').first()
    if not teacher:
        return jsonify({"message": "Teacher not found"}), 404

    student = User.query.filter_by(id=data['student_id'], role='student').first()
    if not student:
        return jsonify({"message": "Student not found"}), 404

    new_task = Task(
        content=data['content'],
        student_id=data['student_id'],
        teacher_id=teacher_id,
        due_date=datetime.strptime(data['due_date'], "%Y-%m-%d"),
        max_points=data['max_points']
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"message": "Task created successfully"}), 201

@app.route('/task/complete/<int:task_id>', methods=['POST'])
def mark_task_completed(task_id):
    data = request.json
    student_id = data.get('student_id')
    
    if not student_id:
        return jsonify({"message": "Missing student_id parameter"}), 400
        
    task = Task.query.get(task_id)
    if not task or task.student_id != int(student_id):
        return jsonify({"message": "Unauthorized or task not found"}), 403

    if not data.get('answer'):
        return jsonify({"message": "Answer is required"}), 400
        
    task.answer = data.get('answer', None)
    task.sent_date = datetime.now()
    task.completed = True

    db.session.commit()
    return jsonify({"message": "Task marked as completed"}), 200

@app.route('/task/grade/<int:task_id>', methods=['POST'])
def grade_task(task_id):
    data = request.json
    teacher_id = data.get('teacher_id')
    
    if not teacher_id:
        return jsonify({"message": "Missing teacher_id parameter"}), 400
        
    task = Task.query.get(task_id)
    if not task or task.teacher_id != int(teacher_id):
        return jsonify({"message": "Unauthorized or task not found"}), 403

    grade = data.get('grade')
    comment = data.get('comment')
    if grade and 0 < int(grade) <= task.max_points and task.completed:
        task.grade = int(grade)
        task.comment = comment if comment else None
        db.session.commit()
        return jsonify({"message": "Task graded successfully"}), 200

    return jsonify({"message": "Invalid action"}), 400

@app.route('/logs', methods=['GET'])
def get_logs():
    admin_id = request.args.get('admin_id')
    
    if not admin_id:
        return jsonify({"message": "Missing admin_id parameter"}), 400
        
    admin = User.query.filter_by(id=admin_id, role='admin').first()
    if not admin:
        return jsonify({"message": "Unauthorized"}), 403

    logs = Log.query.order_by(Log.timestamp.desc()).all()
    log_list = [{
        "id": log.id,
        "user": f"{log.user.name} {log.user.surname}" if log.user else "System",
        "action": log.action,
        "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    } for log in logs]

    return jsonify(log_list)

@app.route('/upload/<int:task_id>', methods=['POST'])
def upload_file(task_id):
    student_id = request.form.get('student_id')
    
    if not student_id:
        return jsonify({"message": "Missing student_id parameter"}), 400
    
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    task = Task.query.filter_by(id=task_id, student_id=student_id).first()
    if not task:
        return jsonify({"message": "Task not found or not assigned to you"}), 404

    if file and allowed_file(file.filename):
        filename = secure_filename(f"{task_id}_{student_id}_{file.filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        file.save(file_path)

        task.file_path = file_path
        db.session.commit()
        return jsonify({"message": "File uploaded", "filename": filename}), 200

    return jsonify({"message": "Invalid file type"}), 400

@app.route('/uploads/<path:filepath>')
def uploaded_file(filepath):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filepath, as_attachment=True)

@app.route('/task/<int:task_id>', methods=['GET'])
def get_task_details(task_id):
    user_id = request.args.get('user_id')
    role = request.args.get('role')
    
    if not user_id or not role:
        return jsonify({"message": "Missing user_id or role parameter"}), 400
    
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"message": "Task not found"}), 404
    
    if (role == 'teacher' and task.teacher_id != int(user_id)) or \
       (role == 'student' and task.student_id != int(user_id)):
        return jsonify({"message": "Unauthorized access"}), 403
    
    task_data = {
        "id": task.id,
        "content": task.content,
        "student_id": task.student_id,
        "teacher_id": task.teacher_id,
        "due_date": task.due_date.strftime("%Y-%m-%d") if task.due_date else None,
        "sent_date": task.sent_date.strftime("%Y-%m-%d %H:%M:%S") if task.sent_date else None,
        "answer": task.answer,
        "completed": task.completed,
        "max_points": task.max_points,
        "grade": task.grade,
        "comment": task.comment,
        "file_path": task.file_path,
        "student_name": f"{task.student.name} {task.student.surname}",
        "teacher_name": f"{task.teacher.name} {task.teacher.surname}"
    }
    
    return jsonify(task_data)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run(debug=True)