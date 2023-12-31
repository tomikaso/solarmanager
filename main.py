# Kunterbunt_Solar_Manager (c) Thomas, March 2023
import math
import requests
from astro import astro
import time
import relais
import temperature
from datetime import datetime, timezone, timedelta
import plotenergy
import constants

# own functions
def runtime(time):
    if time < 60:
        return str(int(time)) + " min"
    else:
        if int(time-int(time/60)*60) > 9:
            return str(int(time / 60)) + ":"+ str(int(time-int(time/60)*60))  + " hr"
        else:
            return str(int(time / 60)) + ":0"+ str(int(time-int(time/60)*60))  + " hr"

# set parameters
relais.init_relais()
relais.plug1_off()
relais.boiler_off()
relais.heatpump_enabled()
api_url = constants.api_url
pathBoiler = constants.pathBoiler
pathHouse = constants.pathHouse
loops = 1
plug1_state = "off"
boiler_state = "off"
heatpump_state = "automatic"
boiler_max = 60
desinfect_target = 57
boiler_hysteresis = 2
desinfect_max_interval = 4

# set variables
minutes_boiler = 0
minutes_plug = 0
sum_solar = 0
sum_load = 0
sum_grid = 0
sum_export = 0
sum_hp_blocked = 0
today_previous = datetime.now(timezone.utc)

# determine last desinfection after restart
solar_status_file = open('/home/solarmanager/Documents/solarstatus.txt', "r")
firstline = solar_status_file.readline()
secondline = solar_status_file.readline()
desinfect_date = secondline.find('desinfection:') + 14
desinfected = datetime.strptime(str(secondline)[desinfect_date:(desinfect_date + 10)],"%d/%m/%Y")
solar_status_file.close()

boiler_state_since = datetime.now()
up_since = datetime.now()
heatpump_appreciated_until = datetime.now()

plug_pic = '<img src="plug_off.png" width=60>'
boiler_pic = '<img src="boiler_off.png" width=60>'
x =  [ time.strftime("%H:%M"), time.strftime("%H:%M")]
xh =  [ time.strftime("%H:%M"), time.strftime("%H:%M")]
x1 = [ time.strftime("%H:%M"), time.strftime("%H:%M")]
y = [45, 45]
yh = [20, 20]
y1 = [1, 1]
y2 = [1, 1]
y3 = [1, 1]
y4 = [1, 1]
y5 = [1, 1]
y6 = [1, 1]
print('Kunterbunt SolarManager')

while True:
    localTime = datetime.now()
    today = datetime.now(timezone.utc)
    astro_data = astro(today)
    status = "online"
    try:
        response = requests.get(api_url, timeout=10)
    except requests.exceptions.ConnectTimeout:
        print("Timed out: switching to save mode")
        status = "save_mode"
    except requests.exceptions.ConnectionError as conerr:
        print("Connection error: switching to save mode")
        print (conerr)
        status = "save_mode"
    except requests.exceptions.RequestException as err:
        print("Request exeption: switching to save mode")
        status = "save_mode"
    if response.status_code != 200:
        print("http_error: switching to save mode")
        print (response.status_code)
        status = "save_mode"
    if status == "online":
        SolarResponse: object = response.json()['siteCurrentPowerFlow']
        if SolarResponse['unit'] == "kW":
         Unit = 1000
        else:
            Unit = 1
        solar = (SolarResponse["PV"])
        solar_power = int(solar['currentPower'] * Unit)
        Load = (SolarResponse["LOAD"])
        LoadPower = int(Load['currentPower'] * Unit)
        GridPower = LoadPower - solar_power
    else:
        solar_power = 0
        LoadPower = 0
        GridPower = 0
    # increment sums
    seconds_since = (today-today_previous).total_seconds()
    today_previous = today
    sum_solar += solar_power / 1000 * seconds_since / 3600
    sum_load += LoadPower / 1000 * seconds_since / 3600
    if GridPower > 0:
        sum_grid += GridPower / 1000 * seconds_since / 3600
    else:
        sum_export += -GridPower / 1000 * seconds_since / 3600

    # sum up plug and boiler time
    if boiler_state == "exceed" or boiler_state == "desinfect":
        minutes_boiler = minutes_boiler + seconds_since / 60
    if plug1_state == "on":
        minutes_plug = minutes_plug + seconds_since / 60
    if heatpump_state == "blocked":
        sum_hp_blocked = sum_hp_blocked + seconds_since / 60

    # reset sums on midnight
    now = datetime.now()
    if (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds() < 180:
        minutes_boiler = 0
        minutes_plug = 0
        sum_hp_blocked = 0
        sum_solar = 0
        sum_load = 0
        sum_grid = 0
        sum_export = 0

    #temperatur ermitteln
    boiler_temp = temperature.read_sensor(pathBoiler)  #measured on top of the boiler
    house_temp = temperature.read_sensor(pathHouse) #living-room

    #determine Heat Pump State blocked: will incereas the sensor-temperature of the heatpump by 2.3K (800kOhm parallel)
    if boiler_temp >= 44 and boiler_temp < 48.5 and astro_data.theo_power <= 3000:  #we still have hot water and no sun
        heatpump_state = "blocked"
        relais.heatpump_blocked()

        #determine Heat Pump State appriciated: will reduce the sensor-temperature of the heatpump by 4.7K (20kOhm in serie)
    if boiler_temp < 48 and astro_data.theo_power >4000 and GridPower < -0.4* astro_data.theo_max:
        heatpump_state = "appreciated"
        heatpump_appreciated_until = datetime.now() + timedelta (minutes=20)
        relais.heatpump_appreciated()

    #determine Heat Pump State automatic #need to heat up, also with non-solar energy, again automatic, when hot.
    if  (boiler_temp < 43.5 or boiler_temp > 48.5)  or \
        (astro_data.theo_power > 3000 and heatpump_state !="appreciated") or \
        (heatpump_state =="appreciated" and heatpump_appreciated_until < datetime.now()):
        heatpump_state = "automatic"
        relais.heatpump_enabled()

    #set new desinfection time (always 8 o'clock UTC)
    if boiler_temp >=  desinfect_target:
        desinfected = today.replace(hour=8)

    #boiler on-condition exceed of energy
    if (status=="online") and (boiler_temp < boiler_max - boiler_hysteresis) and (GridPower < -6500 * astro_data.autum_haze) \
            and boiler_state == "off" and astro_data.theo_power > 5000 and heatpump_state !="appreciated":
        relais.boiler_on()
        boiler_state = "exceed"
        boiler_state_since = datetime.now()
        boiler_pic = '<img src="boiler_on.png" width=60>'
    #    print ('Boiler turned on at: ', boiler_state_since, 'Boiler-Temp:', Boiler_temp)

    # disinfection boiler on: next weekend of if we have 60% of potential radiation
    no_desinfect = datetime.now().replace(tzinfo=None)  - desinfected.replace(tzinfo=None)
    if (boiler_state == "off") and (status=="online") and (no_desinfect.days > desinfect_max_interval) and heatpump_state !="appreciated"  \
        and (astro_data.utctime > 10.5) and (astro_data.utctime < 15) \
        and ((GridPower < - 3000 and astro_data.theo_power > 4000)  or \
            ((no_desinfect.days > desinfect_max_interval + 3) and (astro_data.utctime >11.6) and today.weekday() > 4)):
        relais.boiler_on()
        boiler_state = "desinfect"
        boiler_state_since = datetime.now()
        boiler_pic = '<img src="boiler_desinfect.png" width=60>'
     #   print ('Boiler (desinfect) turned on at: ', boiler_state_since, 'Boiler-Temp:', Boiler_temp)

    #boiler off condition
    if status!="online" \
            or boiler_temp >= boiler_max \
            or (boiler_state == "exceed" and (GridPower > 1200 or solar_power < 4800)) \
            or (boiler_state == "desinfect" and boiler_temp >= desinfect_target)\
            or ((no_desinfect.days <= desinfect_max_interval + 3) and (boiler_state == "desinfect") and (GridPower > 5000 or solar_power < 1500)) \
            or (GridPower > 8000):
        relais.boiler_off()
        boiler_state = "off"
        boiler_state_since = datetime.now()
        boiler_pic = '<img src="boiler_off.png" width=60>'
     #   print ('Boiler turned on off: ', boiler_state_since, 'Boiler-Temp:', Boiler_temp)
    
    #turn on the plug, if energy
    if GridPower < -500 and boiler_state == "off" and astro_data.theo_power > 500:
        relais.plug1_on()
        plug1_state = "on"
        plug_pic = '<img src="plug_on.png" width=60>'
    if GridPower > 100 or boiler_state != "off" or astro_data.theo_power < 400:
        relais.plug1_off()
        plug1_state = "off"
        plug_pic = '<img src="plug_off.png" width=60>'

    # to be sure
    if boiler_state == 'off':
        relais.boiler_off()
    
    #write out status
    statusfile = open('/home/solarmanager/Documents/solarstatus.txt','w')
    Status_str = "\r\n<table><tr><td>" + plug_pic + "<br>" + runtime(minutes_plug) + "</td><td>today: " + str(time.strftime("%d/%m/%Y %H:%M")) + "<br>solar-power: " + str(solar_power)
    Status_str += "<br>grid: " + str(GridPower) + "<br>load: " + str(LoadPower) + "<br>boiler-temp: " + str(boiler_temp) + "<br>house-temp: " + str(house_temp)
    Status_str +=  "<br>solar kwh: " + str(round(sum_solar,2)) + "<br>export kwh: " + str(round(sum_export,2)) +  "<br>heatpump: " + heatpump_state + "</td><td>"
    Status_str +=  "status: " + status + "<br>theoretical radiation: " + str(round(astro_data.theo_power, 1))
    Status_str +=  "<br>max declination: " + str(round(astro_data.maxdeclination,2))+ "<br>last desinfection: " + str(desinfected.strftime("%d/%m/%Y"))
    Status_str +=  "<br>boiler-state-since: " + str(boiler_state_since.strftime("%H:%M")) + "<br>up since: " + str(up_since.strftime("%d/%m/%Y, %H:%M"))
    Status_str +=  "<br>own use kwh: " + str(round(sum_load,2)) + "<br>import kwh: " + str(round(sum_grid,2)) + "<br>" + "heatpump block: " + runtime(sum_hp_blocked)
    Status_str +=  "</td><td>" + boiler_pic + "<br>" + runtime(minutes_boiler) + "</td></tr></table>"
    statusfile.write(Status_str)
    statusfile.close()

    #create power chart
    x1.append(time.strftime("%H:%M"))
    y1.append(LoadPower)
    y2.append(solar_power)
    y3.append(round(astro_data.theo_power, 2))
    if boiler_state != 'off':
        y4.append(400)
    else:
        y4.append(0)
    if plug1_state == 'on':
        y5.append(200)
    else:
        y5.append(0)
    if heatpump_state == 'blocked':
        y6.append(100)
    else:
        if heatpump_state == 'appreciated':
            y6.append(150)
        else:
            y6.append(0)
    if len(x1) > 720:
        y1.pop(0)
        y2.pop(0)
        y3.pop(0)
        y4.pop(0)
        y5.pop(0)
        y6.pop(0)
        x1.pop(0)
    plotenergy.plot_energy(x1, y1, y2, y3, y4, y5, y6, 0, max(max(y3),max(y1))*1.1)

    #create Boiler temperature chart
    x.append(time.strftime("%H:%M"))
    y.append(boiler_temp)
    if len(x) > 720:
        y.pop(0)
        x.pop(0)
    plotenergy.plot_boiler(x, y, math.floor(min(y)*0.95), math.ceil(max(y)*1.05))

    #create house temperature chart
    xh.append(time.strftime("%H:%M"))
    yh.append(house_temp)
    if len(xh) > 720:
        yh.pop(0)
        xh.pop(0)
    plotenergy.plot_house(xh, yh, math.floor(min(yh)*0.97), math.ceil(max(yh)*1.03))

    # blink to tell us, that you are alive for 60 seconds
    for i in range(4):
        relais.led_on() #show checklite_led
        time.sleep(3)
        relais.led_off()
        time.sleep(12)
    # repeat for a long time
relais.plug1_off()
relais.boiler_off()
relais.heatpump_enabled()
print ('Program ended, plugs off')
