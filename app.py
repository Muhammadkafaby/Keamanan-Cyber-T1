from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from functools import wraps
import sqlite3

app = Flask(__name__)
app.jinja_env.autoescape = True  # pastikan autoescape aktif
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'some_secret_key'  # Added for session management
db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'

def sanitize_text(value):
    if any(ch in value for ch in "<>"):
        raise ValueError("Invalid characters")
    return value[:100]

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            session['user_id'] = username
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    # RAW Query
    students = db.session.execute(text('SELECT * FROM student')).fetchall()
    return render_template('index.html', students=students)

@app.route('/add', methods=['POST'])
@login_required
def add_student():
    name = sanitize_text(request.form['name'])
    age_str = sanitize_text(request.form['age'])
    age = int(age_str)
    grade = sanitize_text(request.form['grade'])

    connection = sqlite3.connect('instance/students.db')
    cursor = connection.cursor()

    # RAW Query
    # db.session.execute(
    #     text("INSERT INTO student (name, age, grade) VALUES (:name, :age, :grade)"),
    #     {'name': name, 'age': age, 'grade': grade}
    # )
    # db.session.commit()
    query = f"INSERT INTO student (name, age, grade) VALUES ('{name}', {age}, '{grade}')"
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('index'))


@app.route('/delete/<string:id>')
@login_required
def delete_student(id):
    # RAW Query
    db.session.execute(text(f"DELETE FROM student WHERE id={id}"))
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    if request.method == 'POST':
        name = sanitize_text(request.form['name'])
        age_str = sanitize_text(request.form['age'])
        age = int(age_str)
        grade = sanitize_text(request.form['grade'])

        # RAW Query
        db.session.execute(text(f"UPDATE student SET name='{name}', age={age}, grade='{grade}' WHERE id={id}"))
        db.session.commit()
        return redirect(url_for('index'))
    else:
        # RAW Query
        student = db.session.execute(text(f"SELECT * FROM student WHERE id={id}")).fetchone()
        return render_template('edit.html', student=student)

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
