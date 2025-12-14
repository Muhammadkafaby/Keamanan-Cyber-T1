<?php
    include 'app.php'; 

    if (isset($_GET['id'])) {
        $id = $_GET['id'];
        deleteStudent($id);
    }

?>