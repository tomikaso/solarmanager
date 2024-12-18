# Kunterbunt_Solar_Manager (c) Thomas, February 2024
import math
import requests
from astro import astro
import time
import relais
import temperature
from datetime import datetime, timezone, timedelta
import plotenergy
import constants
import meteo

# own functions
def runtime(minute_display):
    if minute_display < 60:
        return str(int(minute_display)) + " min"
    else:
        if int(minute_display - int(minute_display / 60) * 60) > 9:
            return str(int(minute_display / 60)) + ":" + str(int(minute_display - int(minute_display / 60) * 60)) + " hr"
        else:
            return str(int(minute_display / 60)) + ":0" + str(int(minute_display - int(minute_display / 60) * 60)) + " hr"


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
disinfect_target = 57
boiler_hysteresis = 2
disinfect_max_interval = 4
chart_length = 14

# set variables
minutes_boiler = 0
minutes_plug = 0
sum_solar = 0
sum_load = 0
sum_grid = 0
sum_export = 0
sum_hp_blocked = 0
today_previous = datetime.now(timezone.utc)
meteoOnline = 'false'
meteoString = '<table><td>yet no meteo data</td></table>'
meteoTiming = 0

# determine last disinfection after restart
solar_status_file = open('/home/solarmanager/Documents/solarstatus.txt', "r")
first_line = solar_status_file.readline()
second_line = solar_status_file.readline()
disinfect_date = second_line.find('disinfection:') + 14
disinfected = datetime.strptime(str(second_line)[disinfect_date:(disinfect_date + 10)], "%d/%m/%Y")
solar_status_file.close()

boiler_state_since = datetime.now()
up_since = datetime.now()
heatpump_appreciated_until = datetime.now()

plug_pic = '<img src="plug_off.png" width=60>'
boiler_pic = '<img src="boiler_off.png" width=60>'
x = [time.strftime("%H:%M")]
y = [45]
yh = [20]
y1 = [1]
y2 = [1]
y3 = [1]
y4 = [1]
y5 = [1]
y6 = [1]

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
        print(conerr)
        status = "save_mode"
    except requests.exceptions.RequestException as err:
        print("Request exception: switching to save mode")
        status = "save_mode"
    if response.status_code != 200:
        print("http_error: switching to save mode")
        print(response.status_code)
        status = "save_mode"
    if status == "online":
        SolarResponse: object = response.json()['siteCurrentPowerFlow']
        if SolarResponse['unit'] == "kW":
            Unit = 1000
        else:
            Unit = 1
        solar = (SolarResponse["PV"])
        try:
            solar_power = int(solar['currentPower'] * Unit)
        except KeyError:
            solar_power = 0
            status = "save_mode"
        Load = (SolarResponse["LOAD"])
        try:
            LoadPower = int(Load['currentPower'] * Unit)
        except KeyError:
            LoadPower = 0
            status = "save_mode"
        GridPower = LoadPower - solar_power
    else:
        solar_power = 0
        LoadPower = 0
        GridPower = 0
    # increment sums
    sum_solar += solar_power / 1000 / 60
    sum_load += LoadPower / 1000 / 60
    if GridPower > 0:
        sum_grid += GridPower / 1000 / 60
    else:
        sum_export += -GridPower / 1000 / 60

    # sum up plug and boiler time
    if boiler_state == "exceed" or boiler_state == "disinfect":
        minutes_boiler = minutes_boiler + 1
    if plug1_state == "on":
        minutes_plug = minutes_plug + 1
    if heatpump_state == "blocked":
        sum_hp_blocked = sum_hp_blocked + 1

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

    # get meteo data
    if localTime.minute == 20 or localTime.minute == 50:
        meteo_forcast = meteo.get_meteo()
        if meteo_forcast.status == 'online':
            meteoOnline = 'true'
            meteoString = meteo_forcast.html_string
            if meteo_forcast.timing == 'better today':
                meteoTiming = 1
            elif meteo_forcast.timing == 'better tomorrow':
                meteoTiming = -1
            else:
                meteoTiming = 0
        else:
            meteoOnline = 'false'
            meteoString = meteo_forcast.html_string
            meteoTiming = 0

    # get temperature from sensors
    boiler_temp = temperature.read_sensor(pathBoiler)  # measured on top of the boiler
    house_temp = temperature.read_sensor(pathHouse)  # living-room

    # determine Heat Pump State blocked: will increase the sensor-temperature of the heatpump by 2.3K (800kOhm parallel)
    if 44 <= boiler_temp < 48.5 and astro_data.theo_power <= 2600:  # we still have hot water and no sun
        heatpump_state = "blocked"
        relais.heatpump_blocked()

    # determine Heat Pump State appreciated: will reduce the sensor-temperature of the HP by 4.7K (20kOhm in series)
    if boiler_temp < 48 and astro_data.theo_power > 4000 and GridPower < (-0.4 + meteoTiming/10) * astro_data.theo_max and astro_data.utctime < 12.1:
        heatpump_state = "appreciated"
        heatpump_appreciated_until = datetime.now() + timedelta(minutes=20)
        relais.heatpump_appreciated()

    # determine Heat Pump State automatic #need to heat up, also with non-solar energy, again automatic, when hot.
    if (boiler_temp < 43.5 or boiler_temp > 48.5) or \
            (astro_data.theo_power > 2600 and heatpump_state != "appreciated") or \
            (heatpump_state == "appreciated" and heatpump_appreciated_until < datetime.now()):
        heatpump_state = "automatic"
        relais.heatpump_enabled()

    # set new disinfection time (always 8 o'clock UTC)
    if boiler_temp >= disinfect_target:
        disinfected = today.replace(hour=8)

    # boiler on-condition exceed of energy
    if (status == "online") and (boiler_temp < boiler_max - boiler_hysteresis) and (
            GridPower < (-6400 * astro_data.autum_haze + max(meteoTiming * 400, 0))) \
            and boiler_state == "off" and astro_data.theo_power > 5000 and heatpump_state != "appreciated":
        relais.boiler_on()
        boiler_state = "exceed"
        boiler_state_since = datetime.now()
        boiler_pic = '<img src="boiler_on.png" width=60>'
    #    print ('Boiler turned on at: ', boiler_state_since, 'Boiler-Temp:', Boiler_temp)

    # disinfection boiler on: next weekend of if we have 60% of potential radiation
    no_disinfect = datetime.now().replace(tzinfo=None) - disinfected.replace(tzinfo=None)
    if (boiler_state == "off") and (status == "online") and (
            no_disinfect.days > disinfect_max_interval) and heatpump_state != "appreciated" \
            and (astro_data.utctime > 10.5) and (astro_data.utctime < 15) \
            and ((GridPower < (-0.4 + meteoTiming/10) * astro_data.theo_max and astro_data.theo_power > 3200) or
                 ((no_disinfect.days > disinfect_max_interval + 3) and (
                         astro_data.utctime > 12.6) and today.weekday() > 4)):
        relais.boiler_on()
        boiler_state = "disinfect"
        boiler_state_since = datetime.now()
        boiler_pic = '<img src="boiler_disinfect.png" width=60>'

    # boiler off condition
    if status != "online" \
            or boiler_temp >= boiler_max \
            or (boiler_state == "exceed" and (GridPower > (1200 + max(meteoTiming * 400, 0)) or solar_power < 4800)) \
            or (boiler_state == "disinfect" and boiler_temp >= disinfect_target) \
            or ((no_disinfect.days <= disinfect_max_interval + 3) and (boiler_state == "disinfect") and (
            GridPower > 5000 or solar_power < 1200)) \
            or (GridPower > 8000):
        relais.boiler_off()
        boiler_state = "off"
        boiler_state_since = datetime.now()
        boiler_pic = '<img src="boiler_off.png" width=60>'
    #   print ('Boiler turned on off: ', boiler_state_since, 'Boiler-Temp:', Boiler_temp)

    # turn on the plug, if energy
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

    # write out status
    statusfile = open('/home/solarmanager/Documents/solarstatus.txt', 'w')
    Status_str = "\r\n<table><tr><td>" + plug_pic + "<br>" + runtime(minutes_plug) + "</td><td>today: " + str(
        time.strftime("%d/%m/%Y %H:%M")) + "<br>solar-power: " + str(solar_power)
    Status_str += "<br>grid: " + str(GridPower) + "<br>load: " + str(LoadPower) + "<br>boiler-temp: " + str(
        boiler_temp) + "<br>house-temp: " + str(house_temp)
    Status_str += "<br>solar kwh: " + str(round(sum_solar, 2)) + "<br>export kwh: " + str(
        round(sum_export, 2)) + "</td><td>"
    Status_str += "status: " + status + "<br>theoretical radiation: " + str(round(astro_data.theo_power, 1))
    Status_str += "<br>max declination: " + str(round(astro_data.maxdeclination, 2)) + "<br>last disinfection: " + str(
        disinfected.strftime("%d/%m/%Y"))
    Status_str += "<br>up since: " + str(up_since.strftime("%d/%m/%Y, %H:%M"))
    Status_str += "<br>own use kwh: " + str(round(sum_load, 2)) + "<br>import kwh: " + str(
        round(sum_grid, 2)) + "<br>heatpump: " + heatpump_state
    Status_str += "</td><td>" + boiler_pic + "<br>" + runtime(minutes_boiler) + "</td></tr></table>"
    Status_str += meteoString
    statusfile.write(Status_str)
    statusfile.close()

    # create power chart
    x.append(time.strftime("%H:%M"))
    y1.append(LoadPower)
    y2.append(solar_power)
    y3.append(round(astro_data.theo_power, 2))
    y.append(boiler_temp)
    yh.append(house_temp)
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
    if len(x) > chart_length * 60:
        y1.pop(0)
        y2.pop(0)
        y3.pop(0)
        y4.pop(0)
        y5.pop(0)
        y6.pop(0)
        y.pop(0)  # boiler Temp
        yh.pop(0)  # house Temp
        x.pop(0)  # x-axis for all plots
    plotenergy.plot_energy(x, y1, y2, y3, y4, y5, y6, 0, max(max(y3), max(y1)) * 1.1)
    # create Boiler temperature chart
    plotenergy.plot_boiler(x, y, math.floor(min(y) * 0.95), math.ceil(max(y) * 1.05))
    # create house temperature chart
    plotenergy.plot_house(x, yh, math.floor(min(yh) * 0.97), math.ceil(max(yh) * 1.03))
    # blink to tell us, that you are alive for 60 seconds
    # one long blink is a 1kW, short blink 1/4kw.
    while datetime.now().second < 40:
        relais.led_blink_sun_kw(solar_power)  # indicate solar power with the blinking LED
    # sync with minutes
    while datetime.now().second > 39:
        relais.led_blink_sun_kw(solar_power)
# repeat for a long time
