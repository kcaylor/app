from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.mailgun import Mailgun
from flask.ext.moment import Moment
from flask.ext.mongoengine import MongoEngine
from flask.ext.login import LoginManager
from config import config

boostrap = Bootstrap()
mail = Mailgun()
moment = Moment()
db = MongoEngine()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    boostrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    # attach routes and custom error pages here
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
