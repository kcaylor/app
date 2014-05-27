import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('APP_SECRET')
    MONGOALCHEMY_SERVER_AUTH = False
    MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN')
    MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
    PULSEPOD_MAIL_SENDER = 'PulsePod Admin <postmaster@pulsepod.io>'
    PULSEPOD_MAIL_SUBJECT_PREFIX = '[PulsePod]'
    PULSEPOD_ADMIN = os.environ.get('PULSEPOD_ADMIN')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MONGOALCHEMY_DATABASE = os.environ.get('MONGOALCHEMY_DEV_DATABASE')
    MONGOALCHEMY_SERVER = os.environ.get('MONGOALCHEMY_DEV_SERVER')
    MONGOALCHEMY_USER = os.environ.get('MONGOALCHEMY_DEV_USER')
    MONGOALCHEMY_PORT = os.environ.get('MONGOALCHEMY_DEV_PORT')
    MONGOALCHEMY_PASSWORD = os.environ.get('MONGOALCHEMY_DEV_PASSWORD')


class TestingConfig(Config):
    TESTING = True
    MONGOALCHEMY_DATABASE = 'pulsepod'
    MONGOALCHEMY_SERVER = 'localhost'


class ProductionConfig(Config):
    MONGOALCHEMY_DATABASE = os.environ.get('MONGOALCHEMY_DATABASE')
    MONGOALCHEMY_SERVER = os.environ.get('MONGOALCHEMY_SERVER')
    MONGOALCHEMY_USER = os.environ.get('MONGOALCHEMY_USER')
    MONGOALCHEMY_PORT = os.environ.get('MONGOALCHEMY_PORT')
    MONGOALCHEMY_PASSWORD = os.environ.get('MONGOALCHEMY_PASSWORD')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': TestingConfig
}
