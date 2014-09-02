from flask.ext.login import login_required, current_user
import requests
from flask import current_app, request, render_template
from . import ajax
from app.shared.models.user import make_api_key
from app.shared.models.user import User


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


@ajax.route('/forecast', methods=['POST'])
@login_required
def forecast():
    try:
        lat = request.form["lat"]
        lng = request.form["lng"]
    except KeyError:
        return None
    if 'time' in request.form.keys():
        time = request.form["time"]
    else:
        time = None
    forecast = get_forecast(lat=lat, lng=lng, time=time)
    return render_template(
        'ajax/forecast.html',
        forecast=forecast
    )


@ajax.route('/reset_api_key', methods=['GET'])
@login_required
def reset_api_key():
    user = User.objects(id=request.args['id']).first()
    user.api_key = make_api_key()
    user.save()
    return user.api_key
