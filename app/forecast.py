import requests
from flask import current_app


def get_forecast(lat=None, lng=None, time=None, **flags):
    app = current_app._get_current_object()
    if not app.config['FORECAST_URL'] or not app.config['FORECAST_API_KEY']:
        return {'error': 'invalid forecast.io settings'}
    if lat and lng:
        url = app.config['FORECAST_URL'] + \
            app.config['FORECAST_API_KEY'] + '/' + \
            str(lat) + ',' + str(lng)
        if time:
            url = url + ',' + str(time)
        url = url + '?units=si&exclude=hourly'
        try:
            forecast = requests.get(url=url)
            if forecast.status_code is requests.codes.ok:
                return forecast.json()
            else:
                return None
        except:
                return None
    else:
        return None


# forecast.io icons:
# clear-day, clear-night, rain, snow,
# sleet, wind, fog, cloudy, partly-cloudy-day
# or partly-cloudy-night

def weather_icon(condition=None):

    conditions = {
        'clear-day': 'wi-day-sunny',
        'clear-night': 'wi-night-clear',
        'rain': 'wi-rain',
        'snow': 'wi-snow',
        'fog': 'wi-fog',
        'cloudy': 'wi-cloudy',
        'partly-cloudy-day': 'wi-day-cloudy',
        'partly-cloudy-night': 'wi-night-cloudy',
        'default': ''
    }
    if condition:
        if condition in conditions:
            return conditions[condition]
        else:
            return conditions['default']
    else:
        return conditions['default']
