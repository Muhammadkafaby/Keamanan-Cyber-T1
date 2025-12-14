<?php
// add.php - Form untuk menambahkan data siswa
include 'app.php'; // Menyertakan file koneksi database

// Mengecek apakah form sudah disubmit
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $name = $_POST['name'];
    $age = $_POST['age'];
    $grade = $_POST['grade'];

    // Memanggil fungsi untuk menambah data siswa
    addStudent($name, $age, $grade); // Fungsi addStudent ada di app.php
}

?>

<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tambah Siswa</title>
</head>
<body>
    <h1>Tambah Data Siswa</h1>

    <form method="post" action="">
        <label for="name">Nama:</label>
        <input type="text" id="name" name="name" required>

        <label for="age">Usia:</label>
        <input type="number" id="age" name="age" required>

        <label for="grade">Nilai:</label>
        <input type="text" id="grade" name="grade" required>

        <button type="submit">Tambah Siswa</button>
    </form>

</body>
</html>
