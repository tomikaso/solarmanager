<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
	<title>Solar Manager 2023</title>
<style type="text/css" media="screen">
  body, html {
    padding: 10px 10px 10px 10px;
    background-color: #626C64;
	background-image: url('background_grass.jpg');
    background-repeat: no-repeat;
	background-attachment: fixed;
    background-size: cover;
  }
  div.main_page {
     position: relative;
     display: table;
     width: 640px;
     margin-left: auto;
     margin-right: auto;
     background-color: lightsteelblue;
     color: darkslategray;
 	 font-family: "brandon-grotesque-n7","brandon-grotesque", sans-serif;
     text-align: center;
     font-size: 10pt;
     line-height: 1.4;
   }

  table, th, td {
         border-collapse: collapse;
		 margin:30px;
      }
  td {
         padding-top: 10px;
         padding-bottom: 0px;
         padding-left: 10px;
         padding-right: 10px;
      }
  img { margin:0;
        display:block;
        }
</style>
   <link rel="shortcut icon" type="image/x-icon" href="favicon.ico">
</head>
<body>
  <div  class="main_page">
    <h1>kunterbunt solarmanager</h1>
    <center>
        <?php
          $solstatus = file_get_contents('/home/solarmanager/Documents/solarstatus.txt');
          echo $solstatus;
          echo '<a href="watchdog.php">';
          $watchdog = file_get_contents('/home/solarmanager/Documents/watchdog.txt');
                    echo $watchdog;
          echo '</a>';
        ?>
        <br>
    </center>
    <img src="electricpower.png" alt="Electric power">
	<img src="boiltemp.png" alt="Boiler temperature">
	<img src="housetemp.png" alt="Living room temperature">
  </div>
</body>
    <?php
          header("refresh: 60;");
    ?>
</html>
