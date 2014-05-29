from flask.ext.login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
import datetime


class Data(db.Document):

    time_stamp = db.DateTimeField(db_field='t')
    value = db.FloatField(db_field='v')
    pod_name = db.StringField(db_field='p')
    sensor_name = db.StringField(db_field='s')
    location = db.DictField(db_field='loc')
#    pod = db.ObjectIdField()
#    sensor = db.ObjectIdField()

    meta = {
        'collection': 'data'
    }


class Pod(db.Document):

    name = db.StringField()
    owner = db.StringField()
    pod_id = db.IntField()
    qr = db.StringField()
    imei = db.StringField()
    radio = db.StringField()
    last = db.DateTimeField()
    voltage = db.FloatField()
    mode = db.StringField()
    number = db.StringField()
    nbk_name = db.StringField()
    sensors = db.ListField()
    sids = db.ListField()
    location = db.DictField()
    elevation = db.DictField()
    cellTowers = db.DictField()
    address = db.DictField()
    tags = db.ListField()

    meta = {
        'collection': 'pods'
    }

    def __repr__(self):
        return '<Pod %r>' % self.name

    def get_id(self):
        return unicode(self.id)


class User(UserMixin, db.Document):

    confirmed = db.BooleanField(default=False)
    created_at = db.DateTimeField(
        default=datetime.datetime.now,
        required=True)
    username = db.StringField(max_length=64, unique=True)
    email = db.StringField(max_length=64, unique=True)
    password_hash = db.StringField(max_length=120)
    role = db.StringField(default='user')
    meta = {
        'indexes': ['email', 'username'],
        'collection': 'users'
    }

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.get_id()})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.get_id():
            return False
        self.password = new_password
        self.save()
        return True

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.get_id()})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.get_id():
            return False
        self.confirmed = True
        self.save()
        return True

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        if password:
            self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username

    def __unicode__(self):
        return self.id

    def get_id(self):
        return unicode(self.id)


class AnonymousUser(AnonymousUserMixin):

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    user = User.objects.with_id(user_id)
    return user
