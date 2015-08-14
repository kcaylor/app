from datetime import datetime, timedelta
from flask import render_template, flash, Markup, url_for, jsonify
from flask.ext.login import login_required
from . import admin
from app.shared.models.data import Data
from app.shared.models.sensor import Sensor
from app.shared.models.notebook import Notebook
from app.shared.models.user import User
from app.shared.models.pod import Pod
from app.shared.models.message import Message
from app.decorators import admin_required
from mongoengine import Q
import json

USERS_PER_PAGE = 12
MSG_PER_PAGE = 10


@admin.route('/users')
@admin.route('/users/<int:page>')
@login_required
@admin_required
def users(page=1):
    users = User.objects().order_by('-last_seen').paginate(
        page=page,
        per_page=USERS_PER_PAGE
    )
    return render_template(
        'admin/user_list.html',
        users=users
    )


@admin.route('/messages')
@admin.route('/messages/<int:page>')
@login_required
@admin_required
def messages(page=1):
    # messages = Message.objects().order_by('-time_stamp').paginate(
    #     page=page, per_page=MSG_PER_PAGE
    # )
    last_week = datetime.now() - timedelta(weeks=1)
    message_list = Message.objects(
        time_stamp__gt=last_week
    ).order_by('-time_stamp').limit(100)
    queued_messages = Message.objects(
        status='queued'
    ).order_by('-time_stamp')
    invalid_messages = Message.objects(
        status='invalid'
    ).order_by('-time_stamp')
    for message in queued_messages:
        url = url_for('admin.message_info', _id=message.get_id())
        alert = Markup(
            "Warning: Message <a href=%s>%s</a> is queued \
            and has not been processed." % (url, message.message_id)
        )
        flash(alert, 'warning')
    return render_template(
        'admin/message_list.html',
        current_time=datetime.utcnow(),
        # messages=messages,
        message_list=message_list
    )


@admin.route('/message/<_id>')
@login_required
@admin_required
def message_info(_id):
    message = Message.objects(id=_id).first()
    return render_template(
        'admin/message_info.html',
        current_time=datetime.utcnow(),
        message=message
    )


@admin.route('/gateway_test')
@login_required
@admin_required
def gateway_test():
    gateways = [
        {
            'country': 'Kenya',
            '_id': 'Kenya01',
            'number': '+2540773858828'
        },
        {
            'country': 'Zambia',
            '_id': 'Zambia01',
            'number': '+260971534809',
        },
    ]
    return render_template(
        'admin/gateway_test.html',
        gateways=gateways,
        gateways_json=json.dumps(gateways)
    )


@admin.context_processor
def helper_functions():

    def label_voltage(voltage):
        if voltage is None:
            return 'info'
        if voltage > 3.8:
            return 'success'
        if voltage > 3.6:
            return 'warning'
        return 'danger'

    def message_status(status):
        print status
        if status == 'posted':
            return 'success'
        if status == 'queued':
            return 'warning'
        if status == 'invalid':
            return 'danger'
        if status == 'unknown':
            return 'default'
        if status == 'parsed':
            return 'primary'
        return 'default'

    return dict(
        label_voltage=label_voltage,
        message_status=message_status
    )
