import requests, json

# static data to SMA meteoservice
meteo_sunny = [1, 2, 26, 27]
meteo_cloudy = [3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 29, 30, 31, 32, 33, 34, 36, 37, 38, 39]
meteo_overcast = [5, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 28, 40, 41, 42]

# get sunshine
def get_sunshine(weather_symbol):
    if weather_symbol in meteo_sunny:
        return 'sunny'
    elif weather_symbol in meteo_cloudy:
        return 'cloudy'
    elif weather_symbol in meteo_overcast:
        return 'ovc'
    else:
        return 'undefined'

# get the data
def get_meteo():
    status = 'online'
    try:
        y = requests.get('https://www.meteoschweiz.admin.ch/product/output/versions.json', timeout=10)
        version = json.loads(y.text)
        url = 'https://www.meteoschweiz.admin.ch/product/output/weather-widget/forecast/version__' + version[
            'weather-widget/forecast'] + '/de/863400.json'
        x = requests.get(url, timeout=10)
    except requests.exceptions.ConnectTimeout:
        print("swissmeteo weather timed out.")
        status = 'offline'
    except requests.exceptions.ConnectionError as conerr:
        print("error in connection to swissmeteo weather.")
        status = 'offline'
    except requests.exceptions.RequestException as err:
        print("swissmeteo weather request exception.")
        status = 'offline'
    if y.status_code != 200 or x.status_code != 200 or status == 'offline':
        print("http_error swissmeteo error")
        get_meteo.html_string = '<table><td>meteo service offline</td></table>'
        get_meteo.status = status
        return get_meteo

    payload = json.loads(x.text)
    get_meteo.current_temp = payload['data']['current']['temperature']
    data = payload['data']['current']['temperature']
    symbol = payload['data']['current']['weather_symbol_id']
    forecast_symbol0 = payload['data']['forecasts'][0]['weather_symbol_id']
    forecast_symbol1 = payload['data']['forecasts'][1]['weather_symbol_id']
    forecast_symbol2 = payload['data']['forecasts'][2]['weather_symbol_id']
    get_meteo.current = payload['data']['current']['temperature']
    # meteo-timing
    get_meteo.current = get_sunshine(int(forecast_symbol0))
    get_meteo.plus_24 = get_sunshine(int(forecast_symbol1))
    get_meteo.plus_48 = get_sunshine(int(forecast_symbol2))
    get_meteo.timing = 'neutral'
    if (get_meteo.current == 'sunny' or get_meteo.current == 'cloudy') and get_meteo.plus_24 == 'ovc':
        get_meteo.timing = 'better today'
    if get_meteo.current == 'ovc' and (get_meteo.plus_24 == 'sunny' or get_meteo.plus_24 == 'cloudy'):
        get_meteo.timing = 'better tomorrow'
    html_weather = '<table><tr><td><img src="thermometer.png" alt="temp" width=18></td><td>' + str(data) + '°C</td>'
    html_weather += '<td><img src="weathericons/' + str(forecast_symbol0) + '.svg" alt="symbol">current</td>'
    html_weather += '<td><img src="weathericons/' + str(forecast_symbol1) + '.svg" alt="symbol">+24h</td>'
    html_weather += '<td><img src="weathericons/' + str(forecast_symbol2) + '.svg" alt="symbol">+48h</td>'
    html_weather += '<td><img src="timing.svg" alt="timing">' + get_meteo.timing + '</td>'
    html_weather += '</tr></table>'
    get_meteo.html_string = html_weather
    get_meteo.status = status
    return get_meteo
