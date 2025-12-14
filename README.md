Proyek ini adalah aplikasi web sederhana yang dibuat dengan Flask dan SQLite.

## Fitur
- CRUD sederhana untuk entitas `Student`.
- Templating menggunakan Flask dan Bootstrap.
- Database menggunakan SQLite.

## Teknologi
- **Flask**: Framework web yang digunakan untuk mengembangkan aplikasi ini.
- **Flask SQLAlchemy**: Digunakan untuk ORM dan manajemen database.
- **Bootstrap**: Digunakan untuk styling dasar.

## Persyaratan
- Python 3.6 atau lebih baru
- Virtual environment untuk isolasi paket

## Instalasi

Ikuti langkah-langkah di bawah ini untuk menginstal dan menjalankan proyek ini secara lokal:

1. **Clone repository** (jika diperlukan):
   ```bash
   git clone <repository-url>
   cd project_folder
   ```

2. **Buat virtual environment**:
   ```bash
   python3 -m venv .venv
   ```

3. **Aktifkan virtual environment**:
   ```bash
   source .venv/bin/activate
   ```

4. **Instal dependensi**:
   ```bash
   pip install flask flask_sqlalchemy
   ```

5. **Jalankan aplikasi**:
   ```bash
   python app.py
   ```

6. **Akses aplikasi**:
   Buka browser dan akses:
   ```
   http://127.0.0.1:5000
   ```

## Struktur Proyek
- `app.py`: File utama aplikasi yang berisi logika backend Flask.
- `templates/`: Folder untuk file HTML yang digunakan dalam aplikasi.
