import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('APP_SECRET')
    API_KEY_SALT = os.environ.get('API_KEY_SALT')
    MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN')
    MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
    PULSEPOD_MAIL_SENDER = 'PulsePod Admin <postmaster@pulsepod.io>'
    PULSEPOD_MAIL_SUBJECT_PREFIX = '[PulsePod] '
    PULSEPOD_ADMIN = os.environ.get('PULSEPOD_ADMIN')
    FORECAST_API_KEY = os.environ.get('FORECAST_API_KEY')
    FORECAST_URL = 'https://api.forecast.io/forecast/'
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    # STORMPATH_API_KEY_ID = os.environ.get('STORMPATH_API_KEY_ID')
    # STORMPATH_API_KEY_SECRET = os.environ.get('STORMPATH_API_KEY_SECRET')
    # STORMPATH_APPLICATION = os.environ.get('STORMPATH_APPLICATION')
    XLSX_PATH = 'app/static/xlsx/'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MONGODB_SETTINGS = {
        "DB": os.environ.get('MONGODB_DEV_DATABASE'),
        "USERNAME": os.environ.get('MONGODB_DEV_USER'),
        "PASSWORD": os.environ.get('MONGODB_DEV_PASSWORD'),
        "HOST": os.environ.get('MONGODB_DEV_HOST'),
        "PORT": int(os.environ.get('MONGODB_DEV_PORT'))
    }


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED=False
    MONGODB_SETTINGS = {
        "DB": 'testing',
        "USERNAME": '',
        "PASSWORD": '',
        "HOST": 'localhost',
        "PORT": 27017
    }


class ProductionConfig(Config):
    MONGODB_SETTINGS = {
        "DB": os.environ.get('MONGODB_DATABASE'),
        "USERNAME": os.environ.get('MONGODB_USER'),
        "PASSWORD": os.environ.get('MONGODB_PASSWORD'),
        "HOST": os.environ.get('MONGODB_HOST'),
        "PORT": int(os.environ.get('MONGODB_PORT'))
    }
    XLSX_PATH = '/app/app/static/xlsx/'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
