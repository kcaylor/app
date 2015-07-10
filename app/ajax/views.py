from flask.ext.login import login_required, current_user
from app.decorators import admin_required
import requests
from flask import current_app, request, render_template, jsonify, abort
from . import ajax
from app.shared.models.user import make_api_key
from app.shared.models.user import User
from app.shared.models.sensor import Sensor
from app.shared.models.notebook import Notebook
from app.shared.models.data import Data
from app.shared.models.message import Message
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


def init_message_html(message=None):
    if message:
        info_string = '<span class="text-primary">' + \
            '<strong>' + message.message_content[:2] + '</strong></span>'
        info_string += '<span class="text-danger">' + \
            '<strong>' + message.message_content[2:6] + '</strong></span>'
        info_string += '<span>' + message.message_content[6:] + '</span>'
        info_string += '<br><br><span class="text-primary">Message type: ' + \
            str(message.Message.__class__.__name__) + "</span>"
        info_string += '<br><span class="text-danger">Pod: ' + \
            message.pod.name + '</span>'
        info_string += '<br>Notebook: ' + message.notebook.name + '</span>'
        return info_string
    else:
        return 0


@ajax.route('/message_initialize', methods=['POST'])
@login_required
@admin_required
def message_initialize():
    message = Message.objects(message_id=request.form['message_id']).first()
    try:
        message.init()
    except:
        return "Error initializing message"
    try:
        info_string = init_message_html(message)
    except:
        return "Error creating message html"
    info_string += '<br>Initialized!'
    return info_string


@ajax.route('/message_parse', methods=['POST'])
@login_required
@admin_required
def message_parse():
    message = Message.objects(message_id=request.form['message_id']).first()
    try:
        message.init()
    except:
        return "Error initializing message"
    try:
        info_string = init_message_html(message)
    except:
        return "Error creating message html"
    try:
        message.parse()
    except:
        return "Error parsing message"
    info_string += '<br>Parsed!'
    return info_string


@ajax.route('/message_post', methods=['POST'])
@login_required
@admin_required
def message_post():
    message = Message.objects(message_id=request.form['message_id']).first()
    try:
        message.init()
    except:
        return "Error initializing message"
    info_string = '<span>' + message.message_content[:2] + '</span>'
    info_string += '<span>' + message.message_content[2:] + '</span>'
    info_string += '<br><br>Message type: ' + \
        str(message.Message.__class__.__name__)
    info_string += '<br><span>Pod: ' + message.pod.name + '</span>'
    info_string += '<br>Notebook: ' + message.notebook.name + '</span>'
    info_string += '<br>Posted!'
    return info_string


@ajax.route('/message_delete', methods=['POST'])
@login_required
@admin_required
def message_delete():
    message = Message.objects(message_id=request.form['message_id']).first()
    message.delete()
    return "Message deleted."


@ajax.route('/notebook_delete', methods=['POST'])
@login_required
def notebook_delete():
    notebook = Notebook.objects(id=request.form['notebook_id']).first()
    if current_user.username == notebook.owner.username or \
            current_user.is_administrator():
        if not notebook.pod.current_notebook == notebook:
            notebook.delete()
            return "Notebook deleted."
        else:
            pass
    else:
        abort(403)


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


@ajax.route('/set_nbk_event_sensor', methods=['GET'])
@login_required
def set_nbk_event_sensor():
    # We use the current event resolution and the passed event sensor
    # to set this notebook's event_sensor field. Then we need to update all
    # the data for this notebook's events to specify that they came from
    # the new event_sensor. Future data from the notebook will then post
    # events as coming from the new event_sensor.
    notebook = Notebook.objects(id=request.args['id']).first()
    # The current events are being logged into this sensor:
    this_event = Sensor.objects(id=request.args['sid']).first()
    # Find the event resolution (a bit of a hack):
    [event, resolution] = this_event.name.split('-')
    # Set the new event_sensor's name using the passed argument
    name = request.args['event_sensor'].lower() + '_' + resolution
    # Find this new event_sensor in the database:
    event_sensor = Sensor.objects(name=name).first()
    # event_idx = notebook.sensors.index(event_sensor)
    # notebook.sensors[event_idx] = new_sensor
    # Assign the notebook event_sensor to this sensor:
    notebook.event_sensor = event_sensor
    # sid_idx = notebook.sids.index(event_sensor.sid)
    # notebook.sids[sid_idx] = new_sensor.sid
    # Save the notebook so that this info is permanent:
    notebook.save()
    # Return what we need to make the page right:
    return json.dumps({
        'variable': event_sensor.context + ' ' + event_sensor.variable,
        'unit': event_sensor.unit
    })


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
