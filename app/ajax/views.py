from flask.ext.login import login_required, current_user
import requests
from flask import current_app, request, render_template, jsonify, abort
from . import ajax
from app.shared.models.user import make_api_key
from app.shared.models.user import User
from app.shared.models.sensor import Sensor
from app.shared.models.notebook import Notebook
from app.shared.models.data import Data
import calendar
import datetime
import json


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


@ajax.route('/get_data/<nbk_id>/<sensor_id>', methods=['GET'])
@login_required
def get_data(nbk_id, sensor_id):
    sensor = Sensor.objects(id=sensor_id).first()
    notebook = Notebook.objects(nbk_id=nbk_id).first()
    data = Data.objects(
        notebook=notebook,
        sensor=sensor,
        time_stamp__gt=datetime.datetime(2014, 1, 1, 0, 0, 0)
    ).order_by(
        'time_stamp'
    ).only(
        'time_stamp',
        'value',
    )
    d = {}
    d['name'] = sensor.context + \
        ' ' + sensor.variable + ' [' + sensor.unit + ']'
    d['data'] = []
    for item in data:
        point = {}
        point['x'] = calendar.timegm(item.time_stamp.utctimetuple())
        point['y'] = item.value
        d['data'].append(point)
    print json.dumps(d)
    return jsonify(d)


@ajax.route('/all_data/<nbk_id>', methods=['GET'])
@login_required
def all_data(nbk_id):
    my_response = []
    notebook = Notebook.objects(nbk_id=nbk_id).first()
    for sensor in notebook.sensors:
        d = {}
        d['name'] = sensor.context + ' ' + sensor.variable
        d['units'] = sensor.unit
        d['data'] = []
        data = Data.objects(
            notebook=notebook,
            sensor=sensor
        ).order_by(
            'time_stamp'
        ).only(
            'time_stamp',
            'value',
        )
        for item in data:
            point = {}
            point['x'] = calendar.timegm(item.time_stamp.utctimetuple())
            point['y'] = item.value
            d['data'].append(point)
        my_response.append(d)
    print json.dumps(my_response)
    return jsonify(my_response)