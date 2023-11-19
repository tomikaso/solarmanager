<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
	<title>Solar Manager 2023</title>
<style type="text/css" media="screen">
  body, html {
    padding: 3px 3px 3px 3px;
    background-color: #D8DBE2;
    font-family: Verdana, sans-serif;
    font-size: 12pt;
    text-align: center;
  }
  div.main_page {
    position: relative;
    display: table;
    width: 800px;
    background-color: #AF2244;
    text-align: center;
  }
    </style>
</head>
<body>
  <div  class="main_page">
    <h1>kunterbunty solarmanager</h1>
    <br>
    <h1>Aktueller Status</h1>
<?php
  $zitate = file_get_contents('/home/solarmanager/Documents/solarstatus.txt');
  echo $zitate;
  echo time();
?>
  </div>
</body>
</html>
