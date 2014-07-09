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
        forecast = requests.get(url=url)
        if forecast.status_code is requests.codes.ok:
            return forecast.json()
        else:
            return {'error': forecast.status_code}
    else:
        return {}
