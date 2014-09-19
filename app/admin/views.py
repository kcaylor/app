from datetime import datetime
from flask import render_template, flash, Markup, url_for
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

USERS_PER_PAGE = 10
MSG_PER_PAGE = 10


@admin.route('/users')
@admin.route('/users/<int:page>')
@login_required
@admin_required
def users(page=1):
    users = User.objects().paginate(
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
    messages = Message.objects().order_by('-time_stamp').paginate(
        page=page, per_page=MSG_PER_PAGE
    )
    queued_messages = Message.objects(
        status='queued'
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
        messages=messages
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
        if status is 'parsed':
            return 'success'
        if status is 'queued':
            return 'warning'
        if status is 'invalid':
            return 'danger'
        if status is 'unknown':
            return 'default'
        return 'info'

    return dict(
        label_voltage=label_voltage,
        message_status=message_status
    )
