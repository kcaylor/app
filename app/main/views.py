from datetime import datetime
from flask import render_template, flash
from flask.ext.login import login_required
from . import main
from ..models.pod import Pod
from ..models.data import Data
from ..models.sensor import Sensor
from ..models.notebook import Notebook
from ..forecast import get_forecast
import uuid


@main.route('/')
@login_required
def index():
    notebooks = Notebook.objects().order_by('-last').only(
        'name',
        'voltage',
        'last'
    )
    return render_template(
        'index.html',
        current_time=datetime.utcnow(),
        notebooks=notebooks
    )


@main.route('/notebook/<_id>')
@login_required
def notebook_info(_id):
    notebook = Notebook.objects(
        id=_id
        ).first()
    data = Data.objects(
        notebook=notebook
        ).order_by(
            '-time_stamp'
        ).only(
            'time_stamp', 'value', 'variable'
        ).limit(100)
    sensors = Sensor.objects(
        sid__in=notebook.sids
        )
    forecast = get_forecast(
        lat=notebook.lat(),
        lng=notebook.lng())
    if len(data) is 0:
        flash('Waiting for initial data transmission', 'warning')
    return render_template(
        'notebook_info.html',
        current_time=datetime.utcnow(),
        notebook=notebook,
        data=data,
        sensors=sensors,
        json=data.to_json(),
        forecast=forecast
    )


@main.context_processor
def helper_functions():

    def format_price(amount, currency=u'$'):
        return u'{1}{0:.2f}'.format(amount, currency)

    def label_voltage(voltage):
        if voltage is None:
            return 'info'
        if voltage > 3.8:
            return 'success'
        if voltage > 3.6:
            return 'warning'
        return 'danger'

    return dict(
        format_price=format_price,
        label_voltage=label_voltage
    )
