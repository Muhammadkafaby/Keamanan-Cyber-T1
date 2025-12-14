<?php
ini_set('display_errors', 1);
error_reporting(E_ALL);

// Koneksi ke database (sesuaikan dengan konfigurasi Anda)
try {
    $db = new PDO('sqlite:students.db');
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION); // Menampilkan error jika terjadi kesalahan
} catch (PDOException $e) {
    echo "Koneksi ke database gagal: " . $e->getMessage();
    exit;
}

// Fungsi untuk mengambil semua data siswa
function getAllStudents($db) {
    $query = "SELECT * FROM students";
    $result = $db->query($query);

    // Periksa apakah query berhasil
    if ($result === false) {
        echo "Query gagal: " . $db->errorInfo()[2];  // Menampilkan pesan error dari database
        return [];
    }

    return $result->fetchAll(PDO::FETCH_ASSOC);
}

// Fungsi untuk menampilkan data siswa dalam bentuk HTML
function displayStudents($students) {
    echo '<div class="container mt-5">';
    echo '<h2>Daftar Siswa</h2>';
    echo '<table class="table table-striped">';
    echo '<thead><tr><th>ID</th><th>Nama</th><th>Usia</th><th>Nilai</th></tr></thead>';
    echo '<tbody>';
    foreach ($students as $student) {
        echo "<tr>";
        echo "<td>" . htmlspecialchars($student['id']) . "</td>";  // Menggunakan htmlspecialchars untuk keamanan
        echo "<td>" . htmlspecialchars($student['name']) . "</td>";
        echo "<td>" . htmlspecialchars($student['age']) . "</td>";
        echo "<td>" . htmlspecialchars($student['grade']) . "</td>";
        echo "</tr>";
    }
    echo '</tbody>';
    echo '</table>';
    echo '</div>';
}

// Fungsi untuk menambahkan siswa baru
function addStudent($db, $name, $age, $grade) {
    $query = "INSERT INTO students (name, age, grade) VALUES (:name, :age, :grade)";
    $stmt = $db->prepare($query);

    // Bind parameter dan eksekusi query
    $stmt->bindParam(':name', $name);
    $stmt->bindParam(':age', $age);
    $stmt->bindParam(':grade', $grade);
    
    if ($stmt->execute()) {
        return true;
    } else {
        return false;
    }
}

// Proses untuk menambah data siswa baru melalui formulir
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Ambil data dari formulir
    $name = $_POST['name'];
    $age = $_POST['age'];
    $grade = $_POST['grade'];

    // Tambahkan siswa ke database
    if (addStudent($db, $name, $age, $grade)) {
        echo "<div class='container mt-3 alert alert-success'>Siswa baru berhasil ditambahkan!</div>";
    } else {
        echo "<div class='container mt-3 alert alert-danger'>Gagal menambahkan siswa baru.</div>";
    }
}

// Ambil semua data siswa
$students = getAllStudents($db);

// Tampilkan data siswa jika ada
if (empty($students)) {
    echo "<p class='container mt-3'>Tidak ada data siswa yang tersedia.</p>";
} else {
    displayStudents($students);
}
?>

<!-- Menambahkan Bootstrap CDN di bagian bawah file HTML -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daftar Siswa</title>
    <!-- Menggunakan Bootstrap 4 CDN -->
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-pzjw8f+ua7Kw1TIq0g9WvwJ5v3zmbw7a8D2yJrxO5C+HfS0tL6BQyyEd4G7Wfgpn" crossorigin="anonymous">
</head>
<body>

    <div class="container mt-5">
        <h2>Tambah Siswa Baru</h2>
        <form action="" method="POST">
            <div class="form-group">
                <label for="name">Nama</label>
                <input type="text" id="name" name="name" class="form-control" required>
            </div>
            <div class="form-group">
                <label for="age">Usia</label>
                <input type="number" id="age" name="age" class="form-control" required>
            </div>
            <div class="form-group">
                <label for="grade">Nilai</label>
                <input type="text" id="grade" name="grade" class="form-control" required>
            </div>
            <button type="submit" class="btn btn-primary">Tambah Siswa</button>
        </form>
    </div>

    <!-- Bagian Konten akan ditampilkan di sini, menggunakan PHP di atas -->

    <!-- Menggunakan Bootstrap JS dan Popper.js -->
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js" integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zyL5R53i2o5ch1f9SO4f3gT5I5LJ6Tp+fA9ETp1L" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js" integrity="sha384-pzjw8f+ua7Kw1TIq0g9WvwJ5v3zmbw7a8D2yJrxO5C+HfS0tL6BQyyEd4G7Wfgpn" crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js" integrity="sha384-pzjw8f+ua7Kw1TIq0g9WvwJ5v3zmbw7a8D2yJrxO5C+HfS0tL6BQyyEd4G7Wfgpn" crossorigin="anonymous"></script>

</body>
</html>
