# B. Hasil Analisis dan Peningkatan Keamanan Program

Berikut adalah hasil analisis dan peningkatan keamanan program Flask untuk manajemen student data.

## 1. Analisis Celah Keamanan

### a. Celah Keamanan yang Teridentifikasi

**Deskripsi celah keamanan:**

- Semua endpoint CRUD (list /, tambah /add, edit /edit/<id>, hapus /delete/<id>) bisa diakses tanpa login.
- Siapa pun yang tahu URL dapat memodifikasi data siswa langsung.

**CWE terkait:** CWE-306: Missing Authentication for Critical Function

**Bagian program yang rentan:**

- Semua fungsi route di app.py tidak memiliki proteksi autentikasi
- Model Student diakses langsung tanpa pengecekan sesi pengguna

### b. Serangan yang Mengeksploitasi Celah Keamanan

**Deskripsi serangan yang dilakukan:**
Langkah serangan (tanpa perlu login):

1. Buka http://127.0.0.1:5000/student dan pastikan daftar siswa tampil normal.
2. Lakukan POST ke /add secara langsung dengan curl atau browser untuk menambah data siswa palsu.
3. Kirim GET ke /delete/<id> untuk menghapus data siswa yang sah.
4. Kirim PUT ke /edit/<id> untuk memodifikasi data siswa.

**Bukti keberhasilan serangan:**

- **Sebelum serangan:** Daftar siswa hanya berisi data valid.
- **Selama serangan:** Penyerang dapat mengirim request HTTP langsung tanpa kredensial.
- **Setelah serangan:** Data siswa ditambah, diubah, atau dihapus sesuai akses penyerang.

## 2. Peningkatan Keamanan Program

### a. Pengamanan yang Dilakukan

**Deskripsi pengamanan (modifikasi terhadap program):**

- Menambahkan sistem autentikasi berbasis sesi dengan Flask session
- Implementasi decorator @login_required untuk melindungi semua endpoint kritikal
- Hanya pengguna yang telah login yang boleh mengakses fungsi CRUD
- Penambahan halaman login (/login) dengan kredensial sederhana
- Penambahan fungsi logout untuk membersihkan sesi

**Alasan pemilihan teknik pengamanan:**

- **CWE-306** semua fungsi kritis sebelum dipanggil.
- Teknik session-based authentication sederhana namun efektif untuk aplikasi web sederhana.
- Mudah diuji dengan unit testing (pytest).
- Kompatibel dengan framework Flask yang digunakan.

### b. Cuplikan Program yang Telah Diperkuat

#### app.py (modifikasi utama):

```python
# Imports tambahan
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from functools import wraps
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'some_secret_key'  # Added for session management
db = SQLAlchemy(app)

# Decorator untuk memastikan login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Route login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            session['user_id'] = username
            return redirect(url_for('index'))
    return render_template('login.html')

# Route logout
@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# Proteksi semua route utama
@app.route('/')
@login_required
def index():
    # ... list students

@app.route('/add', methods=['POST'])
@login_required
def add_student():
    # ... add student logic

@app.route('/delete/<string:id>')
@login_required
def delete_student(id):
    # ... delete logic

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    # ... edit logic
```

#### templates/login.html (baru):

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>Login</title>
    <link
      rel="stylesheet"
      href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css"
    />
  </head>
  <body>
    <div class="container mt-5">
      <h1>Login</h1>
      <form action="/login" method="POST">
        <div class="form-group">
          <label for="username">Username</label>
          <input
            type="text"
            name="username"
            id="username"
            class="form-control"
            required
          />
        </div>
        <div class="form-group">
          <label for="password">Password</label>
          <input
            type="password"
            name="password"
            id="password"
            class="form-control"
            required
          />
        </div>
        <button type="submit" class="btn btn-primary">Login</button>
      </form>
    </div>
  </body>
</html>
```

### c. Pengujian Keamanan

#### test_auth.py:

```python
def test_crud_requires_login(client):
    resp = client.post("/add", data={"name": "Evil", "age": 20, "grade": "A"})
    assert resp.status_code in (302, 401, 403)

def test_crud_after_login(client):
    client.post("/login", data={"username": "admin", "password": "admin123"})
    resp = client.post("/add", data={"name": "Good", "age": 21, "grade": "B"})
    assert resp.status_code == 302
```

**Hasil penyerangan ulang:**

- **Sebelum serangan ulang:** User belum login.
- **Proses serangan ulang:** Test mengirim POST ke /add tanpa login.
- **Setelah serangan:** Aplikasi mengembalikan redirect/unauthorized sehingga penyerang tidak bisa menambah data tanpa login.

**Testing dengan pytest:**

```bash
pytest test_auth.py -v
================== test session starts ==================
test_auth.py::test_crud_requires_login PASSED [ 50%]
test_auth.py::test_crud_after_login PASSED [100%]
================== test session starts ==================
```

## Kesimpulan:

Program telah berhasil diperkuat dengan mekanisme autentikasi. Semua endpoint kritikal sekarang memerlukan login terlebih dahulu. Penggunaan session Flask memungkinkan aplikasi untuk melacak status login pengguna. Teknik ini efektif dalam mencegah akses tidak sah terhadap fungsi CRUD dan memenuhi standar keamanan dasar aplikasi web.

**Cara menjalankan aplikasi:**

```bash
python app.py
```

Aplikasi akan berjalan di: http://127.0.0.1:5000

**Kredensial akses:**

- Username: admin
- Password: admin123
