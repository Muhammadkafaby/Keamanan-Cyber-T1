"""
Flask Student Management App - SECURED VERSION
Versi yang telah diperkuat keamanannya dari SQL Injection
"""

from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from functools import wraps
import sqlite3
import re

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

# ============================================================
# FUNGSI VALIDASI INPUT - DITAMBAHKAN UNTUK KEAMANAN
# ============================================================

def validate_input(value, field_name, max_length=100, allowed_pattern=r'^[a-zA-Z0-9\s\-\.]+$'):
    """
    Validasi input untuk mencegah SQL Injection dan serangan lainnya
    
    Args:
        value: nilai input dari user
        field_name: nama field untuk pesan error
        max_length: panjang maksimum yang diizinkan
        allowed_pattern: regex pattern karakter yang diizinkan
    
    Returns:
        string yang sudah divalidasi
    
    Raises:
        ValueError jika input tidak valid
    """
    if not value:
        raise ValueError(f"{field_name} tidak boleh kosong")
    
    # Batasi panjang input
    if len(value) > max_length:
        raise ValueError(f"{field_name} maksimal {max_length} karakter")
    
    # Cek karakter yang diizinkan
    if not re.match(allowed_pattern, value):
        raise ValueError(f"{field_name} mengandung karakter tidak valid")
    
    # Blokir karakter berbahaya untuk XSS
    if any(ch in value for ch in "<>"):
        raise ValueError(f"{field_name} mengandung karakter berbahaya")
    
    return value.strip()

def validate_id(id_value):
    """
    Validasi ID harus berupa integer positif
    """
    try:
        id_int = int(id_value)
        if id_int <= 0:
            raise ValueError("ID harus positif")
        return id_int
    except (ValueError, TypeError):
        raise ValueError("ID tidak valid")

def validate_age(age_value):
    """
    Validasi umur harus integer antara 1-150
    """
    try:
        age_int = int(age_value)
        if age_int < 1 or age_int > 150:
            raise ValueError("Umur harus antara 1-150")
        return age_int
    except (ValueError, TypeError):
        raise ValueError("Umur tidak valid")

def validate_grade(grade_value):
    """
    Validasi grade hanya A, B, C, D, E, F
    """
    valid_grades = ['A', 'B', 'C', 'D', 'E', 'F', 'A+', 'A-', 'B+', 'B-', 'C+', 'C-', 'D+', 'D-']
    grade = grade_value.strip().upper()
    if grade not in valid_grades:
        raise ValueError(f"Grade harus salah satu dari: {', '.join(valid_grades)}")
    return grade

# ============================================================
# VERSI LAMA (RENTAN) - DIKOMENTARI
# ============================================================
# def sanitize_text(value):
#     if any(ch in value for ch in "<>"):
#         raise ValueError("Invalid characters")
#     return value[:100]

# ============================================================
# DECORATOR LOGIN
# ============================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ============================================================
# ROUTES
# ============================================================

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
    # SECURED: Query statis tanpa input user, aman dari SQL Injection
    students = db.session.execute(text('SELECT * FROM student')).fetchall()
    return render_template('index.html', students=students)

# ============================================================
# ADD STUDENT - SECURED VERSION
# ============================================================

@app.route('/add', methods=['POST'])
@login_required
def add_student():
    try:
        # SECURED: Validasi input dengan fungsi validasi yang ketat
        name = validate_input(request.form['name'], 'Name', max_length=100)
        age = validate_age(request.form['age'])
        grade = validate_grade(request.form['grade'])

        connection = sqlite3.connect('instance/students.db')
        cursor = connection.cursor()

        # ============================================================
        # VERSI LAMA (RENTAN SQL INJECTION) - DIKOMENTARI
        # ============================================================
        # query = f"INSERT INTO student (name, age, grade) VALUES ('{name}', {age}, '{grade}')"
        # cursor.execute(query)
        
        # ============================================================
        # VERSI BARU (SECURED) - PARAMETERIZED QUERY
        # ============================================================
        # Menggunakan placeholder ? untuk mencegah SQL Injection
        # Input user diperlakukan sebagai DATA, bukan bagian dari perintah SQL
        query = "INSERT INTO student (name, age, grade) VALUES (?, ?, ?)"
        cursor.execute(query, (name, age, grade))
        
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('index'))
    
    except ValueError as e:
        return f"Error: {str(e)}", 400
    except Exception as e:
        return f"Database error: {str(e)}", 500

# ============================================================
# DELETE STUDENT - SECURED VERSION
# ============================================================

# VERSI LAMA (RENTAN) - DIKOMENTARI
# @app.route('/delete/<string:id>')
# @login_required
# def delete_student(id):
#     # RAW Query - RENTAN SQL INJECTION
#     db.session.execute(text(f"DELETE FROM student WHERE id={id}"))
#     db.session.commit()
#     return redirect(url_for('index'))

# VERSI BARU (SECURED)
@app.route('/delete/<int:id>')  # SECURED: Menggunakan <int:id> bukan <string:id>
@login_required
def delete_student(id):
    try:
        # SECURED: Validasi ID harus integer positif
        safe_id = validate_id(id)
        
        # ============================================================
        # VERSI LAMA (RENTAN SQL INJECTION) - DIKOMENTARI
        # ============================================================
        # db.session.execute(text(f"DELETE FROM student WHERE id={id}"))
        
        # ============================================================
        # VERSI BARU (SECURED) - PARAMETERIZED QUERY
        # ============================================================
        # Menggunakan parameter binding :id untuk mencegah SQL Injection
        db.session.execute(
            text("DELETE FROM student WHERE id = :id"),
            {"id": safe_id}
        )
        db.session.commit()
        return redirect(url_for('index'))
    
    except ValueError as e:
        return f"Error: {str(e)}", 400
    except Exception as e:
        return f"Database error: {str(e)}", 500

# ============================================================
# EDIT STUDENT - SECURED VERSION
# ============================================================

# VERSI LAMA (RENTAN) - DIKOMENTARI
# @app.route('/edit/<int:id>', methods=['GET', 'POST'])
# @login_required
# def edit_student(id):
#     if request.method == 'POST':
#         name = sanitize_text(request.form['name'])
#         age_str = sanitize_text(request.form['age'])
#         age = int(age_str)
#         grade = sanitize_text(request.form['grade'])
#         # RAW Query - RENTAN SQL INJECTION
#         db.session.execute(text(f"UPDATE student SET name='{name}', age={age}, grade='{grade}' WHERE id={id}"))
#         db.session.commit()
#         return redirect(url_for('index'))
#     else:
#         # RAW Query - RENTAN SQL INJECTION
#         student = db.session.execute(text(f"SELECT * FROM student WHERE id={id}")).fetchone()
#         return render_template('edit.html', student=student)

# VERSI BARU (SECURED)
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    try:
        # SECURED: Validasi ID
        safe_id = validate_id(id)
        
        if request.method == 'POST':
            # SECURED: Validasi semua input
            name = validate_input(request.form['name'], 'Name', max_length=100)
            age = validate_age(request.form['age'])
            grade = validate_grade(request.form['grade'])

            # ============================================================
            # VERSI LAMA (RENTAN SQL INJECTION) - DIKOMENTARI
            # ============================================================
            # db.session.execute(text(f"UPDATE student SET name='{name}', age={age}, grade='{grade}' WHERE id={id}"))
            
            # ============================================================
            # VERSI BARU (SECURED) - PARAMETERIZED QUERY
            # ============================================================
            # Menggunakan parameter binding untuk semua nilai
            db.session.execute(
                text("UPDATE student SET name = :name, age = :age, grade = :grade WHERE id = :id"),
                {"name": name, "age": age, "grade": grade, "id": safe_id}
            )
            db.session.commit()
            return redirect(url_for('index'))
        else:
            # ============================================================
            # VERSI LAMA (RENTAN SQL INJECTION) - DIKOMENTARI
            # ============================================================
            # student = db.session.execute(text(f"SELECT * FROM student WHERE id={id}")).fetchone()
            
            # ============================================================
            # VERSI BARU (SECURED) - PARAMETERIZED QUERY
            # ============================================================
            student = db.session.execute(
                text("SELECT * FROM student WHERE id = :id"),
                {"id": safe_id}
            ).fetchone()
            return render_template('edit.html', student=student)
    
    except ValueError as e:
        return f"Error: {str(e)}", 400
    except Exception as e:
        return f"Database error: {str(e)}", 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
