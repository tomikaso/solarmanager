<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <link rel="stylesheet" href="solarstyle.css">
    <script src="solarScript.js"></script>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
	<title>Solar Manager 2023</title>
   <link rel="shortcut icon" type="image/x-icon" href="favicon.ico">
</head>
<body onload="showSlides(0)">
  <div  class="main_page">
    <a class="prev" onclick="plusSlides(-1)">&#10094;</a>
    <a class="next" onclick="plusSlides(1)">&#10095;</a>
    <center>
        <?php
          $solstatus = file_get_contents('/home/solarmanager/Documents/solarstatus.txt');
          echo $solstatus;
          echo '<a href="watchdog.php">';
          $watchdog = file_get_contents('/home/solarmanager/Documents/watchdog.txt');
                    echo $watchdog;
          echo '</a>';
        ?>
    </center>
    <div class="headline" id="headline"><h1>kunterbunt solarmanager</h1>
            <object id="status" class="obj" width="700" type="text/html" ></object>
    </div>
	  <img id="power1" width="800" height="400"  src="electricpower.png" alt="Electric power">
      <img id="boil1" width="800" height="400"   src="boiltemp.png" alt="Boiler temperature">
      <img id="house1" width="800" height="400"  src="housetemp.png" alt="Living room temperature">
  </div>
</body>
    <?php
          header("refresh: 60;");
    ?>
</html>
