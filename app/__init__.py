from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.mailgun import Mailgun
from flask.ext.moment import Moment
from flask.ext.mongoengine import MongoEngine
from flask.ext.login import LoginManager
from flask.ext.assets import Environment, Bundle

from config import config

boostrap = Bootstrap()
mail = Mailgun()
moment = Moment()
db = MongoEngine()
assets = Environment()

login_manager = LoginManager()
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
    db.init_app(app)
    login_manager.init_app(app)
    # assets.init_app(app)

    # coffee = Bundle(
    #     'coffee/test.coffee',
    #     filters=['coffeescript', 'yui_js'],
    #     output='js/app.js'
    # )
    # assets.register('coffee_app', coffee)

    # stylus = Bundle(
    #     'stylus/test.styl',
    #     filters=['stylus', 'yui_js'],
    #     output='css/test.css'
    # )
    # assets.register('stylus_app', stylus)

    # attach routes and custom error pages here
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .edit import edit as edit_blueprint
    app.register_blueprint(edit_blueprint, url_prefix='/edit')

    return app
