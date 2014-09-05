from datetime import datetime
from flask import render_template, flash, Markup, url_for, abort
from flask.ext.login import login_required, current_user
from . import main
from app.shared.models.data import Data
from app.shared.models.sensor import Sensor
from app.shared.models.notebook import Notebook
from app.shared.models.user import User
from app.shared.models.pod import Pod
from app.shared.models.message import Message
from app.decorators import admin_required
from mongoengine import Q


# @main.before_app_request
# def before_request():
#     if not current_user.is_authenticated():
#         return redirect(url_for('auth.login'))
NBK_PER_PAGE = 5
MSG_PER_PAGE = 10


@main.route('/')
@login_required
def index():
    unconfirmed_owned = Q(confirmed=False) & Q(owner=current_user.get_id())
    unconfirmed_notebooks = Notebook.objects(
        unconfirmed_owned
    ).order_by('-last').only(
        'name',
        'voltage',
        'last',
        'observations',
        'owner',
        'public',
    )
    for notebook in unconfirmed_notebooks:
        url = url_for('main.notebook_info', _id=notebook.get_id())
        message = Markup(
            "Your new notebook, <a href=%s>%s</a> needs to be confirmed."
            % (url, notebook.name)
        )
        flash(message, 'warning')
    return render_template('index.html')


@main.route('/messages')
@main.route('/messages/<int:page>')
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
        url = url_for('main.message_info', _id=message.get_id())
        alert = Markup(
            "Warning: Message <a href=%s>%s</a> is queued \
            and has not been processed." % (url, message.message_id)
        )
        flash(alert, 'warning')
    return render_template(
        'main/message_list.html',
        current_time=datetime.utcnow(),
        messages=messages
    )


@main.route('/notebooks')
@main.route('/notebooks/<int:page>')
@login_required
def notebooks(page=1):
    with_obs_owned = Q(observations__gt=0) & Q(owner=current_user.get_id())
    notebooks = Notebook.objects(
        with_obs_owned
    ).order_by('-last').only(
        'name',
        'voltage',
        'last',
        'observations',
        'owner',
        'public',
    ).paginate(page=page, per_page=NBK_PER_PAGE)
    unconfirmed_owned = Q(confirmed=False) & Q(owner=current_user.get_id())
    unconfirmed_notebooks = Notebook.objects(
        unconfirmed_owned
    ).order_by('-last').only(
        'name',
        'voltage',
        'last',
        'observations',
        'owner',
        'public',
    )
    for notebook in unconfirmed_notebooks:
        url = url_for('main.notebook_info', _id=notebook.get_id())
        message = Markup(
            "Your new notebook, <a href=%s>%s</a> needs to be confirmed."
            % (url, notebook.name)
        )
        flash(message, 'warning')
    return render_template(
        'user_notebook_list.html',
        title="%s's Notebooks" %
        current_user.username if 'username' in dir(current_user) else 'Guest',
        current_time=datetime.utcnow(),
        notebooks=notebooks,
        new_notebooks=''
    )


@main.route('/public')
@main.route('/public/<int:page>')
@login_required
def public(page=1):
    with_obs_public = Q(observations__gt=0) & Q(public=True)
    notebooks = Notebook.objects(
        with_obs_public
    ).order_by('-last').only(
        'name',
        'voltage',
        'last',
        'observations',
        'owner',
        'public'
    ).paginate(page=page, per_page=NBK_PER_PAGE)
    return render_template(
        'public_notebook_list.html',
        title="Public Notebooks",
        current_time=datetime.utcnow(),
        notebooks=notebooks
    )


@main.route('/user/<username>')
@login_required
def user(username):
    user = User.objects(username=username).first()
    if user is None:
        abort(404)
    notebooks = Notebook.objects(owner=user)
    pods = Pod.objects(owner=user)
    data = Data.objects(owner=user)
    return render_template(
        'user.html',
        user=user,
        pods=pods,
        notebooks=notebooks,
        data=data
    )


@main.route('/message/<_id>')
@login_required
@admin_required
def message_info(_id):
    message = Message.objects(id=_id).first()
    return render_template(
        'main/message_info.html',
        current_time=datetime.utcnow(),
        message=message
    )


@main.route('/notebook/<_id>')
@login_required
def notebook_info(_id):
    notebook = Notebook.objects(
        id=_id
    ).first()
    # Should really do this as an AJAX:
    notebook.xls()
    data = Data.objects(
        notebook=notebook
    ).first()
    sensors = Sensor.objects(
        sid__in=notebook.sids
    )
    current_data = {}
    for sensor in sensors:
        current_value = Data.objects(
            notebook=notebook,
            sensor=sensor).order_by('-time_stamp').first()
        if current_value:
            current_data[sensor.get_id()] = current_value.value
        else:
            current_data[sensor.get_id()] = None
    if not data:
        flash('Waiting for initial data transmission', 'warning')
    return render_template(
        'notebook_info.html',
        current_time=datetime.utcnow(),
        notebook=notebook,
        # data=data,  # No need to return data, because AJAX.
        sensors=sensors,
        current_data=current_data
    )


@main.route('/map')
@login_required
def map():
    notebooks = Notebook.objects(observations__gt=0).order_by('-last').only(
        'name',
        'location',
        'nbk_id',
    )
    return render_template(
        'map.html',
        notebooks=notebooks
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
