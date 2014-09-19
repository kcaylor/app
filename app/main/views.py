from datetime import datetime
from flask import render_template, flash, Markup, url_for, abort
from flask.ext.login import login_required, current_user
from . import main
from app.shared.models.data import Data
from app.shared.models.sensor import Sensor
from app.shared.models.notebook import Notebook
from app.shared.models.user import User
from app.shared.models.pod import Pod
from mongoengine import Q


NBK_PER_PAGE = 5
PODS_PER_PAGE = 10


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/pods')
@main.route('/pods/<int:page>')
@login_required
def pods(page=1):
    if current_user.is_administrator():
        with_obs_owned = None
    else:
        with_obs_owned = Q(observations__gt=0) & Q(owner=current_user.get_id())
    pods = Pod.objects(
        with_obs_owned
    ).order_by('-last').only(
        'name',
        'owner',
        'mode'
    ).paginate(
        page=page, per_page=PODS_PER_PAGE
    )
    return render_template(
        'main/pod_list.html',
        pods=pods
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
    # Don't show user information to anyone but the user and the admin:
    if not current_user.username == username and \
            not current_user.role == 'admin':
        abort(404)
    else:
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


@main.route('/pod/<_id>')
@login_required
def pod_info(_id):
    pod = Pod.objects(id=_id).first()
    # Only let pod owners or administrators look at pods:
    if not pod.owner.username == current_user.username and \
            not current_user.role == 'admin':
        abort(404)
    return render_template(
        'main/pod_info.html',
        current_time=datetime.utcnow(),
        pod=pod
    )


@main.route('/notebook/<_id>')
@login_required
def notebook_info(_id):
    notebook = Notebook.objects(
        id=_id
    ).first()
    # Check if this notebook is public. If it is, then anyone can see it.
    if notebook.public is False:
        # Only let notebook owners or administrators look at this notebook:
        if not notebook.owner == current_user or \
                not current_user.role == 'admin':
            abort(404)
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
