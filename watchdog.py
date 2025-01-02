import time
from datetime import datetime, timezone
import os, shutil

# function to get sums out of the status
def get_value(html_string, tag_name):
    value_start = html_string.find(tag_name)+ len (tag_name)
    value_end = html_string.find("<", value_start)
    return str(secondline)[value_start: value_end]


watchdog_file = open('/home/solarmanager/Documents/solarstatus.txt', "r")
firstline = watchdog_file.readline()
secondline = watchdog_file.readline()
time_start = secondline.find('today:')+7
last_time = str(secondline)[time_start:(time_start+16)]
watchdog_file.close()
now = datetime.now()
history_copy = ""

#evaluate solarmanager actuality
datetime_object = datetime.strptime(last_time,"%d/%m/%Y %H:%M")
uptime_diff = datetime.now()-datetime_object

#write out status
watchdog_file = open('/home/solarmanager/Documents/watchdog.txt', 'w')
Status_str = "\r\n<p>Last Check: " + str(time.strftime("%d/%m/%Y %H:%M")) + " Uptime-difference: " + str(uptime_diff.seconds) + "</p>"
watchdog_file.write(Status_str)
watchdog_file.close()

#delete logfile if midnight
if now.hour == 0 and now.minute < 11:
    file_to_delete = open('/home/solarmanager/Documents/watchlog.txt', 'w')
    file_to_delete.close()

#copy graphs into the history folder
if now.hour == 20 and now.minute < 3:
    target = "/var/www/html/history/electricpower" + str(time.strftime("%Y%m%d")) + ".png"
    shutil.copy("/var/www/html/electricpower.png", target)
    target = "/var/www/html/history/housetemp" + str(time.strftime("%Y%m%d")) + ".png"
    shutil.copy("/var/www/html/housetemp.png", target)
    target = "/var/www/html/history/boiltemp" + str(time.strftime("%Y%m%d")) + ".png"
    shutil.copy("/var/www/html/boiltemp.png", target)
    history_copy ="Three graphs copied. <br>"

#copy status of the day into the history folder
if now.hour == 23 and now.minute > 48 and now.minute < 53:
# calculate the sum-html-file
    statushtml = "<table><td><img width='24' height='24'  src='calendar.png'>" + str( get_value(secondline, "today: "))[0:10] + "</td>"
    statushtml +="<td><img width='24' height='24'  src='sun.png'>" + get_value(secondline, "solar kwh: ") + " kWh</td>"
    statushtml +="<td><img width='24' height='24'  src='plug.png'>" + get_value(secondline, "own use kwh: ") + " kWh</td>"
    statushtml +="<td><img width='24' height='24'  src='pole.png'>" + get_value(secondline, "import kwh: ") + " kWh</td>"
    statushtml +="<td><img width='24' height='24'  src='flame.png'>" + get_value(secondline, 'img src="boiler_off.png" width=60><br>') + "</td>"
    statushtml +="<td><img width='24' height='24'  src='plug_on.png'>" + get_value(secondline, 'img src="plug_off.png" width=60><br>') + "</td></table>"
# write out the file
    status_file = open("/var/www/html/history/solarsum" + str(time.strftime("%Y%m%d")) + ".html", 'w')
    status_file.write(statushtml)
    status_file.close()

#write out log
watchdog_file = open('/home/solarmanager/Documents/watchlog.txt', 'a+')
if 600 < uptime_diff.seconds < 3000:
    Status_str = "\r\n<b>Failed, restarting now: " + str(time.strftime("%d/%m/%Y %H:%M")) + " Uptime-difference: " + str(uptime_diff.seconds) + "</b><br>"
else:
    Status_str = "\r\nLast Check: " + str(time.strftime("%d/%m/%Y %H:%M")) + " Uptime-difference: " + str(uptime_diff.seconds) + "<br>" + history_copy
watchdog_file.write(Status_str)
watchdog_file.close()

#reboot after 10 minutes
if 600 < uptime_diff.seconds < 3000:
    os.system("sudo reboot")
