from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.mailgun import Mailgun
from flask.ext.moment import Moment
from flask.ext.wtf import CsrfProtect
from utils import weather_icon
from config import config
from pymongo import ReadPreference
from slacker import Slacker
import os

from app.shared.models import db, login_manager

slack = Slacker(os.getenv('SLACK_API_TOKEN'))
boostrap = Bootstrap()
mail = Mailgun()
moment = Moment()
csrf = CsrfProtect()

# Create an rq queue from rq and worker.py:
from rq import Queue
from worker import conn

# Set up the worker queues:
mqtt_q = Queue(connection=conn)  # This is the queue for MQTT pubs
xlsx_q = Queue(connection=conn)  # This is the queue for xlxs jobs

login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
login_manager.login_message = \
    'Give your data a pulse by logging in or signing up!'
login_manager.login_message_category = "info"


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    boostrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    # Initialize MongoEngine (for all the mongo goodness)
    from mongoengine import connect
    host = config[config_name]().MONGODB_SETTINGS['HOST']
    connect(
        db='pulsepod-restore',
        host=host
    )
    if config_name is 'testing':
        db.init_app(app)
        db.read_preference = ReadPreference.PRIMARY_PREFERRED

    login_manager.init_app(app)
    csrf.init_app(app)

    # attach routes and custom error pages here
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .edit import edit as edit_blueprint
    app.register_blueprint(edit_blueprint, url_prefix='/edit')

    from .ajax import ajax as ajax_blueprint
    app.register_blueprint(ajax_blueprint, url_prefix='/ajax')

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    # add in view function (context_processors)
    app.jinja_env.globals.update(weather_icon=weather_icon)

    return app
