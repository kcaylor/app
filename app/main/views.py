from datetime import datetime
from flask import render_template, flash, Markup, url_for
from flask.ext.login import login_required, current_user
from . import main
from app.shared.models.data import Data
from app.shared.models.sensor import Sensor
from app.shared.models.notebook import Notebook
from app.forecast import get_forecast
from mongoengine import Q


# @main.before_app_request
# def before_request():
#     if not current_user.is_authenticated():
#         return redirect(url_for('auth.login'))


@main.route('/')
@login_required
def index():
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
    )
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
        'notebook_list.html',
        title="%s's Notebooks" %
        current_user.username if 'username' in dir(current_user) else 'Guest',
        current_time=datetime.utcnow(),
        notebooks=notebooks,
        new_notebooks=''
    )


@main.route('/public')
@login_required
def public():
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
    )
    return render_template(
        'notebook_list.html',
        title="Public Notebooks",
        current_time=datetime.utcnow(),
        notebooks=notebooks
    )


@main.route('/notebook/<_id>')
@login_required
def notebook_info(_id):
    notebook = Notebook.objects(
        id=_id
    ).first()
    notebook.xls()
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
        # json=data.to_json(),
        forecast=forecast
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
