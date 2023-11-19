<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
	<title>Solar Manager 2023</title>
<style type="text/css" media="screen">
  body, html {
    background-color: #626C64;
	background-image: url('08Pfannenstil.jpg');
	background-repeat: no-repeat;
    background-attachment: fixed;
    background-size: cover;
    font-family: "brandon-grotesque-n7","brandon-grotesque", sans-serif;
    font-style: normal;
    font-weight: 200;
    font-size: 11pt;
    text-align: center;
    padding: 10px 10px 10px 10px;
  }
  div.main_page {
    position: relative;
    display: table;
    width: 640px;
    margin-left: auto;
    margin-right: auto;
    background-color: lightsteelblue;
    text-align: center;
  }

  table, th, td {
         border-collapse: collapse;
		 margin:20px;
      }
      th, td {
         padding-top: 10px;
         padding-bottom: 0px;
         padding-left: 10px;
         padding-right: 10px;
      }
       </style>
</head>
<body>
  <div  class="main_page">
    <h1>My watchdog  <a href="index.php">back</a></h1>
    <img src="watchgoose.jpg" alt="watchgoose" width=400>
    <center>
        <?php
          $watchdog = file_get_contents('/home/solarmanager/Documents/watchlog.txt');
                    echo $watchdog;
          header("refresh: 180;");
        ?>
    </center>
  </div>
</body>
</html>
