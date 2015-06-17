import os

basedir = os.path.abspath(os.path.dirname(__file__))


def mongo_url(db_settings=None, replica_set=None):

    if db_settings['USERNAME'] is '':
        return 'mongodb://' + db_settings['HOST'] + \
            ':' + str(db_settings['PORT']) + \
            '/' + db_settings['DB']
    elif replica_set is None:
        return 'mongodb://' + db_settings['USERNAME'] + \
            ':' + db_settings['PASSWORD'] + \
            '@' + db_settings['HOST'] + \
            ':' + str(db_settings['PORT']) + \
            '/' + db_settings['DB']
    else:
        return 'mongodb://' + db_settings['USERNAME'] + \
            ':' + db_settings['PASSWORD'] + \
            '@' + db_settings['HOST'] + \
            '/' + db_settings['DB'] + \
            '?replicaSet=' + replica_set


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
    DB_SETTINGS = {
        "DB": os.environ.get('MONGODB_DEV_DATABASE'),
        "USERNAME": os.environ.get('MONGODB_DEV_USER'),
        "PASSWORD": os.environ.get('MONGODB_DEV_PASSWORD'),
        "HOST": os.environ.get('MONGODB_DEV_HOST'),
        "PORT": int(os.environ.get('MONGODB_DEV_PORT'))
    }
    MONGODB_HOST = mongo_url(db_settings=DB_SETTINGS)


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    DB_SETTINGS = {
        "DB": 'testing',
        "USERNAME": '',
        "PASSWORD": '',
        "HOST": 'localhost',
        "PORT": 27017
    }
    MONGODB_HOST = mongo_url(db_settings=DB_SETTINGS)


class ProductionConfig(Config):
    # Production settings must include replica sets.
    DB_SETTINGS = {
        "DB": os.environ.get('MONGODB_DATABASE'),
        "USERNAME": os.environ.get('MONGODB_USER'),
        "PASSWORD": os.environ.get('MONGODB_PASSWORD'),
        "HOST": os.environ.get('MONGODB_HOST'),
    }
    REPLICA_SET = os.environ.get('MONGODB_REPLICA_SET')
    XLSX_PATH = '/app/app/static/xlsx/'
    MONGODB_HOST = mongo_url(db_settings=DB_SETTINGS, replica_set=REPLICA_SET)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
