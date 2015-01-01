<?php

$dbServer = "server.com";
$dbUser = "username";
$dbPassword = "password";
$dbDatabase = "dbname";

$con = mysqli_connect($dbServer, $dbUser, $dbPassword, $dbDatabase);

// Check connection
if (mysqli_connect_errno($con))
{
  echo "Failed to connect to MySQL: " . mysqli_connect_error();
  echo "<br>Params: $dbServer, $dbUser, $dbPassword, $dbDatabase";
}
else
  echo "Connection OK";
?>
