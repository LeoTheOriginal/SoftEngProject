from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from flask_bcrypt import Bcrypt
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import InputRequired, Length, ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///changeItXD.db'
app.config['SECRET_KEY'] = 'trzebazmienic'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)

    student = db.relationship('User', foreign_keys=[student_id], backref='tasks')
    teacher = db.relationship('User', foreign_keys=[teacher_id])

    def __repr__(self):
        return f'<Task {self.content} assigned by {self.teacher.name} to {self.student.name}>'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.id
    
class RegisterForm(FlaskForm):
    name = StringField('name', validators=[InputRequired(), Length(min=4, max=50)] , render_kw={"placeholder": "Name"})
    surname = StringField('surname', validators=[InputRequired(), Length(min=4, max=50)] , render_kw={"placeholder": "Surname"})
    email = StringField('email', validators=[InputRequired(), Length(min=4, max=50)]  , render_kw={"placeholder": "Email"})
    password = PasswordField('password', validators=[InputRequired(), Length(min=4, max=50)] , render_kw={"placeholder": "Password"})
    role = SelectField('role', choices=[('student', 'Uczeń'), ('teacher', 'Nauczyciel')], validators=[InputRequired()])
    submit = SubmitField('Register')

    def validate_email(self, email):
        existing_user_email = User.query.filter_by(email=email.data).first()
        if existing_user_email:
            raise ValidationError('Email already in use')
    

class LoginForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Length(min=4, max=50)] , render_kw={"placeholder": "Email"})
    password = PasswordField('password', validators=[InputRequired(), Length(min=4, max=50)] , render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')

class TaskForm(FlaskForm):
    content = StringField('Treść zadania', validators=[InputRequired(), Length(min=4, max=200)])
    student_id = SelectField('Wybierz ucznia', coerce=int, validators=[InputRequired()])
    submit = SubmitField('Dodaj zadanie')

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.student_id.choices = [(student.id, f"{student.name} {student.surname}") for student in User.query.filter_by(role='student').all()]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))

    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(
            name=form.name.data, 
            surname=form.surname.data, 
            email=form.email.data, 
            password=hashed_password,
            role=form.role.data
        )
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'teacher':
        return redirect(url_for('teacher_dashboard'))
    else:
        return redirect(url_for('student_dashboard'))

@app.route('/teacher_dashboard', methods=['GET', 'POST'])
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        return redirect(url_for('dashboard'))

    form = TaskForm()
    form.student_id.choices = [(student.id, f"{student.name} {student.surname}") for student in User.query.filter_by(role='student').all()]

    if form.validate_on_submit():
        new_task = Task(
            content=form.content.data, 
            student_id=form.student_id.data,
            teacher_id=current_user.id
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('teacher_dashboard'))

    tasks = Task.query.all()
    return render_template('teacher_dashboard.html', form=form, tasks=tasks)

@app.route('/student_dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        return redirect(url_for('dashboard'))

    tasks = Task.query.filter_by(student_id=current_user.id).all()
    return render_template('student_dashboard.html', tasks=tasks)

@app.route('/task/complete/<int:task_id>', methods=['POST'])
def mark_task_completed(task_id):
    task = Task.query.get(task_id)
    if task:
        task.completed = 1
        db.session.commit()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)