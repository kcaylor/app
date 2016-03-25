import os

basedir = os.path.abspath(os.path.dirname(__file__))


def make_mongo_uri(
        host='localhost',
        port=27017,
        database='default',
        replica_set=None,
        username=None,
        password=None):
    uri = 'mongodb://'
    if username is not None and password is not None:
        uri += username + ':' + password + '@'
    if ',' in host:
        host = host.split(',')
    if not isinstance(host, basestring):
        if port is not None:
            host = [x + ':' + str(port) for x in host]
        uri += ",".join(host)
    else:
        uri += host
        if port is not None:
            uri += ':' + str(port)
    if database is not None:
        uri += '/' + database
    if replica_set is not None:
        uri += '?replicaSet=' + replica_set
    return uri


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
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_URL = 'https://api.twilio.com/2010-04-01/Accounts/'
    TWILIO_NUMBER = os.getenv('TWILIO_NUMBER')
    # REDIS_URL = os.environ.get('REDIS_DEV_URL')
    # BROKER_URL = REDIS_URL
    # CELERY_RESULT_BACKEND = REDIS_URL

    # STORMPATH_API_KEY_ID = os.environ.get('STORMPATH_API_KEY_ID')
    # STORMPATH_API_KEY_SECRET = os.environ.get('STORMPATH_API_KEY_SECRET')
    # STORMPATH_APPLICATION = os.environ.get('STORMPATH_APPLICATION')
    XLSX_PATH = 'app/static/xlsx/'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    PYMONGO_HOST = make_mongo_uri(
        host=os.environ.get('MONGO_DEV_HOST'),
        port=int(os.environ.get('MONGO_DEV_PORT')),
        database=os.environ.get('MONGO_DEV_DBNAME'),
        username=os.environ.get('MONGO_DEV_USERNAME'),
        password=os.environ.get('MONGO_DEV_PASSWORD'),
    )
    MONGODB_SETTINGS = {
        # "DB": os.environ.get('MONGO_DEV_DBNAME'),
        # "USERNAME": os.environ.get('MONGO_DEV_USERNAME'),
        # "PASSWORD": os.environ.get('MONGO_DEV_PASSWORD'),
        # "HOST": os.environ.get('MONGO_DEV_HOST'),
        # "PORT": int(os.environ.get('MONGO_DEV_PORT'))
        "HOST": make_mongo_uri(
            host=os.environ.get('MONGO_DEV_HOST'),
            port=int(os.environ.get('MONGO_DEV_PORT')),
            database=os.environ.get('MONGO_DEV_DBNAME'),
            username=os.environ.get('MONGO_DEV_USERNAME'),
            password=os.environ.get('MONGO_DEV_PASSWORD'),
        )
    }


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    MONGODB_SETTINGS = {
        "DB": 'testing',
        "HOST": 'localhost',
        "PORT": 27017
    }


class ProductionConfig(Config):
    XLSX_PATH = '/app/app/static/xlsx/'
    # Production settings must include replica sets.
    MONGO_URI = make_mongo_uri(
        host=os.environ.get('MONGO_HOST'),
        port=None,  # port is defined in MONGO_HOST for replica sets
        database=os.environ.get('MONGO_DBNAME'),
        username=os.environ.get('MONGO_USERNAME'),
        password=os.environ.get('MONGO_PASSWORD'),
        replica_set=os.environ.get('MONGO_REPLICASET')
    )
    PYMONGO_HOST = make_mongo_uri(
        host=os.environ.get('MONGO_HOST'),
        port=None,  # port is defined in MONGO_HOST for replica sets
        database=os.environ.get('MONGO_DBNAME'),
        username=os.environ.get('MONGO_USERNAME'),
        password=os.environ.get('MONGO_PASSWORD'),
        replica_set=os.environ.get('MONGO_REPLICASET')
    )
    MONGODB_SETTINGS = {
        "HOST": make_mongo_uri(
            host=os.environ.get('MONGO_HOST'),
            port=None,  # port is defined in MONGO_HOST for replica sets
            database=os.environ.get('MONGO_DBNAME'),
            username=os.environ.get('MONGO_USERNAME'),
            password=os.environ.get('MONGO_PASSWORD'),
            replica_set=os.environ.get('MONGO_REPLICASET')
        )
    }
    # REDIS_URL = os.environ.get('REDIS_PROD_URL')
    # BROKER_URL = REDIS_URL
    # CELERY_RESULT_BACKEND = REDIS_URL

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
