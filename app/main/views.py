from datetime import datetime
from flask import render_template, flash
from flask.ext.login import login_required
from . import main
from ..models import Pod, Data, Sensor


@main.route('/')
@login_required
def index():
    pods = Pod.objects().order_by('-last').only(
        'name',
        'nbk_name',
        'voltage',
        'last'
    )
    return render_template(
        'index.html',
        current_time=datetime.utcnow(),
        pods=pods
    )


@main.route('/pods/<name>')
@login_required
def pod_info(name):
    pod = Pod.objects(name=name).first()
    data = Data.objects(pod_name=name).order_by('-t').limit(50)
    sensors = Sensor.objects(sid__in=pod.sids)
    if pod.notebook <= 1:
        flash('This pod needs to be deployed', 'warning')
    if pod.notebook > 1 and len(data) is 0:
        flash('Waiting for initial data transmission', 'warning')
    return render_template(
        'pod_info.html',
        current_time=datetime.utcnow(),
        pod=pod,
        data=data,
        sensors=sensors
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
