"""Ajax views for pulsepod app."""
from flask.ext.login import login_required, current_user
from app.decorators import admin_required
import requests
from flask import current_app, request
from flask import render_template, jsonify, abort, url_for
from . import ajax
from app.shared.models.user import make_api_key
from app.shared.models.user import User
from app.shared.models.sensor import Sensor
from app.shared.models.notebook import Notebook
from app.shared.models.data import Data
from app.shared.models.message import Message
from tasks import create_xls_notebook
import calendar
import datetime
import json


def get_forecast(lat=None, lng=None, time=None, **flags):
    """Get the forecast for this notebook."""
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
    """Initialize the message html."""
    if message:
        info_string = '<span class="text-primary">' + \
            '<strong>' + message.message_content[:2] + '</strong></span>'
        info_string += '<span class="text-danger">' + \
            '<strong>' + message.message_content[2:6] + '</strong></span>'
        info_string += '<span>' + message.message_content[6:60] + '...</span>'
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
    """Initialize the message."""
    message = Message.objects(id=request.form['message_id']).first()
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
    """Parse the message html."""
    message = Message.objects(id=request.form['message_id']).first()
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
    """Post the message html."""
    message = Message.objects(id=request.form['message_id']).first()
    message.init()
    message.parse()
    try:
        message.post()
    except:
        return "Error posting message"
    info_string = '<span>' + message.message_content[:2] + '</span>'
    info_string += '<span>' + message.message_content[2:60] + '...</span>'
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
    """Delete the message html."""
    message = Message.objects(id=request.form['message_id']).first()
    message.delete()
    return "Message deleted."


@ajax.route('/notebook_delete', methods=['POST'])
@login_required
@admin_required
def notebook_delete():
    """Delete the notebook."""
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


@ajax.route('/notebook_merge', methods=['POST'])
@login_required
@admin_required
def notebook_merge():
    """Merge the notebook."""
    notebook = Notebook.objects(id=request.form['notebook_id']).first()
    if current_user.username == notebook.owner.username or \
            current_user.is_administrator():
        if not notebook.pod.current_notebook == notebook:
            n_merged_data = Data.objects(notebook=notebook).count()
            Data.objects(notebook=notebook).update(
                set__notebook=notebook.pod.current_notebook)
            notebook.pod.current_notebook.observations += n_merged_data
            notebook.pod.current_notebook.save()
            notebook.observations = 0
            notebook.save()
            return "{value}".format(
                value=notebook.pod.current_notebook.observations)
        else:
            pass
    else:
        abort(403)


@ajax.route('/gateway_test', methods=['POST'])
@login_required
@admin_required
def gateway_test():
    """Test the gateway."""
    # Build a twilio client
    from twilio.rest import TwilioRestClient
    number = request.form['number']
    if '+' not in number:
        number = '+' + number
    print number
    print current_app.config['TWILIO_NUMBER']
    content = request.form['description'] + ' Test Message'
    account = current_app.config['TWILIO_ACCOUNT_SID']
    token = current_app.config['TWILIO_AUTH_TOKEN']
    client = TwilioRestClient(account, token)
    message = client.messages.create(
        to=number,
        from_=current_app.config['TWILIO_NUMBER'],
        body=content)
    response = {
        'sid': message.sid,
        'content': message.body,
        'status': message.status
    }
    return jsonify(**response)


@ajax.route('/gateway_test_check', methods=['POST'])
@login_required
@admin_required
def gateway_test_check():
    """Check to see that the gateway has been tested."""
    from twilio.rest import TwilioRestClient
    account = current_app.config['TWILIO_ACCOUNT_SID']
    token = current_app.config['TWILIO_AUTH_TOKEN']
    client = TwilioRestClient(account, token)
    message = client.messages.get(request.form['sid'])
    return message.status


@ajax.route('/forecast', methods=['POST'])
@login_required
def forecast():
    """Retrieve a forecast for a specific lat/lon."""
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
    """Reset the user API key."""
    user = User.objects(id=request.args['id']).first()
    user.api_key = make_api_key()
    user.save()
    return user.api_key


@ajax.route('/set_nbk_event_sensor', methods=['GET'])
@login_required
def set_nbk_event_sensor():
    """Set the current notebook's event sensor."""
    # We use the current event resolution and the passed event sensor
    # to set this notebook's event_sensor field.
    notebook = Notebook.objects(nbk_id=request.args['nbk_id']).first()
    # The current events are being logged into this sensor:
    this_event = Sensor.objects(id=request.args['sid']).first()
    # Find the event resolution (a bit of a hack):
    [event, resolution] = this_event.name.split('-')
    # Set the new event_sensor's name using the passed argument
    name = request.args['event_sensor'].lower() + '_' + resolution
    # Find this new event_sensor in the database:
    event_sensor = Sensor.objects(name=name).first()
    # Assign the notebook event_sensor to this sensor:
    notebook.event_sensor = event_sensor
    # Save the notebook so that this info is permanent:
    notebook.save()
    response = {
        'variable': event_sensor.context + ' ' + event_sensor.variable,
        'unit': event_sensor.unit
    }
    # Return what we need to make the page right:
    return jsonify(**response)


@ajax.route('/status/<task_id>')
def taskstatus(task_id):
    """Get the task status for <task_id>."""
    task = create_xls_notebook.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'url': task.info.get('url', 0)
            # 'current': task.info.get('current', 0),
            # 'total': task.info.get('total', 1),
            # 'status': task.info.get('status', '')
        }
        # if 'result' in task.info:
        #    response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


@ajax.route('/create_notebook_xls', methods=['POST'])
@login_required
def create_notebook_xls():
    """Inititate xlsx notebook generation."""
    nbk_id = request.form["nbk_id"]
    task = create_xls_notebook.delay(nbk_id=nbk_id)
    return jsonify({}), 202, {'Location': url_for('.taskstatus',
                                                  task_id=task.id)}


@ajax.route('/get_data/<nbk_id>/<sensor_id>', methods=['GET'])
@login_required
def get_data(nbk_id, sensor_id):
    """Get data for <nbk_id> and <sensor_id>, returned as json."""
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
    """Get all data for <nbk_id>, returned as json."""
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
