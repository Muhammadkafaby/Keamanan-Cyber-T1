"""
Flask Student Management App - SECURED VERSION (IDOR Fixed)
Versi yang telah diperkuat dari kerentanan IDOR dengan:
- Role-Based Access Control (RBAC)
- Ownership Validation
"""

from flask import Flask, render_template, request, redirect, url_for, session, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from functools import wraps
import sqlite3
import re

app = Flask(__name__)
app.jinja_env.autoescape = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'some_secret_key'
db = SQLAlchemy(app)

# ============================================================
# MODEL - DITAMBAHKAN FIELD UNTUK RBAC DAN OWNERSHIP
# ============================================================

class User(db.Model):
    """Model User dengan role untuk RBAC"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # Dalam produksi: gunakan hash!
    role = db.Column(db.String(20), default='user')  # 'admin' atau 'user'
    
    def __repr__(self):
        return f'<User {self.username}>'

class Student(db.Model):
    """Model Student dengan owner_id untuk ownership validation"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10), nullable=False)
    # DITAMBAHKAN: Field untuk tracking ownership
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    def __repr__(self):
        return f'<Student {self.name}>'

# ============================================================
# FUNGSI VALIDASI INPUT (dari versi sebelumnya)
# ============================================================

def validate_input(value, field_name, max_length=100, allowed_pattern=r'^[a-zA-Z0-9\s\-\.]+$'):
    if not value:
        raise ValueError(f"{field_name} tidak boleh kosong")
    if len(value) > max_length:
        raise ValueError(f"{field_name} maksimal {max_length} karakter")
    if not re.match(allowed_pattern, value):
        raise ValueError(f"{field_name} mengandung karakter tidak valid")
    if any(ch in value for ch in "<>"):
        raise ValueError(f"{field_name} mengandung karakter berbahaya")
    return value.strip()

def validate_id(id_value):
    try:
        id_int = int(id_value)
        if id_int <= 0:
            raise ValueError("ID harus positif")
        return id_int
    except (ValueError, TypeError):
        raise ValueError("ID tidak valid")

def validate_age(age_value):
    try:
        age_int = int(age_value)
        if age_int < 1 or age_int > 150:
            raise ValueError("Umur harus antara 1-150")
        return age_int
    except (ValueError, TypeError):
        raise ValueError("Umur tidak valid")

def validate_grade(grade_value):
    valid_grades = ['A', 'B', 'C', 'D', 'E', 'F', 'A+', 'A-', 'B+', 'B-', 'C+', 'C-', 'D+', 'D-']
    grade = grade_value.strip().upper()
    if grade not in valid_grades:
        raise ValueError(f"Grade harus salah satu dari: {', '.join(valid_grades)}")
    return grade

# ============================================================
# DECORATOR UNTUK AUTHENTICATION DAN AUTHORIZATION
# ============================================================

def login_required(f):
    """Decorator: Cek apakah user sudah login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ============================================================
# DITAMBAHKAN: DECORATOR UNTUK ROLE-BASED ACCESS CONTROL
# ============================================================

def admin_required(f):
    """
    Decorator: Cek apakah user adalah admin
    DITAMBAHKAN untuk mencegah IDOR - hanya admin yang bisa akses
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        # SECURED: Cek role user
        if session.get('role') != 'admin':
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

# ============================================================
# DITAMBAHKAN: FUNGSI UNTUK OWNERSHIP VALIDATION
# ============================================================

def check_ownership(student_id, user_id):
    """
    Cek apakah student dimiliki oleh user tertentu
    DITAMBAHKAN untuk mencegah IDOR
    
    Returns:
        True jika user adalah owner atau admin
        False jika bukan
    """
    # Admin bisa akses semua data
    if session.get('role') == 'admin':
        return True
    
    # Cek ownership
    student = db.session.execute(
        text("SELECT owner_id FROM student WHERE id = :id"),
        {"id": student_id}
    ).fetchone()
    
    if student is None:
        return False
    
    return student[0] == user_id

def require_ownership_or_admin(student_id):
    """
    Helper function untuk validasi ownership atau admin role
    Raise 403 jika tidak berhak
    """
    if session.get('role') == 'admin':
        return True
    
    student = db.session.execute(
        text("SELECT owner_id FROM student WHERE id = :id"),
        {"id": student_id}
    ).fetchone()
    
    if student is None:
        abort(404)  # Not Found
    
    if student[0] != session.get('user_id'):
        abort(403)  # Forbidden - tidak berhak
    
    return True

# ============================================================
# ROUTES - LOGIN/LOGOUT
# ============================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # SECURED: Cek user dari database dengan role
        # Untuk demo, hardcoded users:
        users = {
            'admin': {'password': 'admin123', 'role': 'admin', 'id': 1},
            'user1': {'password': 'user123', 'role': 'user', 'id': 2},
            'user2': {'password': 'user123', 'role': 'user', 'id': 3},
        }
        
        if username in users and users[username]['password'] == password:
            session['user_id'] = users[username]['id']
            session['username'] = username
            session['role'] = users[username]['role']  # DITAMBAHKAN: Simpan role di session
            return redirect(url_for('index'))
        
        return render_template('login.html', error="Invalid credentials")
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()  # Clear semua session data
    return redirect(url_for('login'))

# ============================================================
# ROUTES - INDEX
# ============================================================

@app.route('/')
@login_required
def index():
    # SECURED: User biasa hanya lihat data miliknya, admin lihat semua
    if session.get('role') == 'admin':
        students = db.session.execute(text('SELECT * FROM student')).fetchall()
    else:
        # User biasa hanya lihat data miliknya
        students = db.session.execute(
            text('SELECT * FROM student WHERE owner_id = :owner_id'),
            {"owner_id": session.get('user_id')}
        ).fetchall()
    
    return render_template('index.html', students=students, role=session.get('role'))

# ============================================================
# ADD STUDENT - SECURED VERSION
# ============================================================

@app.route('/add', methods=['POST'])
@login_required
def add_student():
    try:
        name = validate_input(request.form['name'], 'Name', max_length=100)
        age = validate_age(request.form['age'])
        grade = validate_grade(request.form['grade'])

        connection = sqlite3.connect('instance/students.db')
        cursor = connection.cursor()

        # SECURED: Tambahkan owner_id saat insert
        query = "INSERT INTO student (name, age, grade, owner_id) VALUES (?, ?, ?, ?)"
        cursor.execute(query, (name, age, grade, session.get('user_id')))
        
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('index'))
    
    except ValueError as e:
        return f"Error: {str(e)}", 400
    except Exception as e:
        return f"Database error: {str(e)}", 500

# ============================================================
# DELETE STUDENT - SECURED VERSION (IDOR FIXED)
# ============================================================

# VERSI LAMA (RENTAN IDOR) - DIKOMENTARI
# @app.route('/delete/<int:id>')
# @login_required
# def delete_student(id):
#     safe_id = validate_id(id)
#     # RENTAN: Tidak ada pengecekan role atau ownership
#     db.session.execute(
#         text("DELETE FROM student WHERE id = :id"),
#         {"id": safe_id}
#     )
#     db.session.commit()
#     return redirect(url_for('index'))

# VERSI BARU (SECURED) - DENGAN OWNERSHIP CHECK
@app.route('/delete/<int:id>')
@login_required
def delete_student(id):
    try:
        safe_id = validate_id(id)
        
        # ============================================================
        # DITAMBAHKAN: VALIDASI OWNERSHIP ATAU ADMIN ROLE
        # ============================================================
        # Cek apakah user berhak menghapus data ini
        require_ownership_or_admin(safe_id)
        
        # Jika lolos validasi, lakukan delete
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
# EDIT STUDENT - SECURED VERSION (IDOR FIXED)
# ============================================================

# VERSI LAMA (RENTAN IDOR) - DIKOMENTARI
# @app.route('/edit/<int:id>', methods=['GET', 'POST'])
# @login_required
# def edit_student(id):
#     safe_id = validate_id(id)
#     # RENTAN: Tidak ada pengecekan role atau ownership
#     if request.method == 'POST':
#         ...
#         db.session.execute(text("UPDATE student SET ..."))
#     else:
#         student = db.session.execute(text("SELECT * FROM student WHERE id=..."))
#     ...

# VERSI BARU (SECURED) - DENGAN OWNERSHIP CHECK
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    try:
        safe_id = validate_id(id)
        
        # ============================================================
        # DITAMBAHKAN: VALIDASI OWNERSHIP ATAU ADMIN ROLE
        # ============================================================
        require_ownership_or_admin(safe_id)
        
        if request.method == 'POST':
            name = validate_input(request.form['name'], 'Name', max_length=100)
            age = validate_age(request.form['age'])
            grade = validate_grade(request.form['grade'])

            db.session.execute(
                text("UPDATE student SET name = :name, age = :age, grade = :grade WHERE id = :id"),
                {"name": name, "age": age, "grade": grade, "id": safe_id}
            )
            db.session.commit()
            return redirect(url_for('index'))
        else:
            student = db.session.execute(
                text("SELECT * FROM student WHERE id = :id"),
                {"id": safe_id}
            ).fetchone()
            return render_template('edit.html', student=student)
    
    except ValueError as e:
        return f"Error: {str(e)}", 400
    except Exception as e:
        return f"Database error: {str(e)}", 500

# ============================================================
# ADMIN ONLY ROUTES (Contoh penggunaan @admin_required)
# ============================================================

@app.route('/admin/users')
@admin_required  # Hanya admin yang bisa akses
def admin_users():
    """Halaman admin untuk melihat semua users"""
    return "Admin Only: User Management Page"

@app.route('/admin/delete-all', methods=['POST'])
@admin_required  # Hanya admin yang bisa akses
def admin_delete_all():
    """Hapus semua data - hanya admin"""
    db.session.execute(text("DELETE FROM student"))
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
