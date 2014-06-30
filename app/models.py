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
    # pod = db.ObjectIdField()
    # sensor = db.ObjectIdField()

    meta = {
        'collection': 'data'
    }

    def __repr__(self):
        return '<Data %r>' % self.value

    def get_id(self):
        return unicode(self.id)

    @staticmethod
    def generate_fake(count=1000):
        from faker import Faker
        from random import random, randint
        npods = len(Pod.objects())
        nsensors = len(Sensor.objects())
        fake = Faker()
        for i in range(count):
            pod = Pod.objects()[randint(0, npods-1)]
            sensor = Sensor.objects()[randint(0, nsensors-1)]
            data = Data(
                time_stamp=fake.date_time_this_month(),
                sensor_name=sensor.name,
                pod_name=pod.name,
                value=random()*100,
                pod=pod.id,
                sensor=sensor.id
            )
            try:
                data.save()
            except:
                "Data save failed"


class Sensor(db.Document):

    name = db.StringField()
    sid_hex = db.StringField()
    sid = db.IntField(unique=True)
    context = db.StringField()
    variable = db.StringField()
    nbytes = db.IntField()
    fmt = db.StringField()
    byte_order = db.StringField()
    info = db.StringField()
    unit = db.StringField()
    m = db.FloatField()
    b = db.FloatField()
    sensing_chip = db.StringField()

    meta = {
        'collection': 'sensors'
    }

    def __repr__(self):
        return '<Sensor %r>' % self.name

    def get_id(self):
        return unicode(self.id)

    @staticmethod
    def generate_fake(count=100):
        from random import choice, randint, random
        from faker import Faker

        fake = Faker()
        fake.seed(1234)
        for i in range(count):
            sensor = Sensor(
                name=fake.domain_word(),
                sid=randint(1, 256),
                context=fake.domain_word(),
                variable=fake.domain_word(),
                nbytes=choice([2, 4, 8, 12, 16]),
                fmt=choice(['x', 'c', 'b', 'B', '?', 'h', 'H',
                            'i', 'I', 'l', 'L', 'q', 'Q', 'f',
                            'd', 's', 'p', 'P']),
                byteorder='<',
                info=fake.catch_phrase(),
                unit='b/s',
                m=random(),
                b=random(),
            )
            try:
                sensor.save()
            except:
                "Sensor save failed"


class Notebook(db.Document):

    name = db.StringField(db_field='nbk_name')
    pod_id = db.ObjectIdField(db_field='_id_pod')
    notebook = db.IntField(db_field='_notebook')
    elevation = db.DictField()
    sensors = db.ListField()
    sids = db.ListField()
    location = db.DictField()
    cellTowers = db.DictField()
    address = db.DictField()

    meta = {
        'collection': 'pods_notebooks'
    }

    def __repr__(self):
        return '<Notebook %r>' % self.name

    def get_id(self):
        return unicode(self.id)


class Pod(db.Document):

    name = db.StringField()
    owner = db.StringField()
    pod_id = db.IntField()
    qr = db.StringField()
    imei = db.StringField()
    radio = db.StringField()
    created_at = db.DateTimeField(
        default=datetime.datetime.now,
        required=True)
    voltage = db.FloatField()
    mode = db.StringField()
    number = db.StringField()
    nbk_name = db.StringField()
    tags = db.ListField()
    last = db.DateTimeField()
    notebook = db.IntField(db_field='_notebook')
    elevation = db.DictField()
    sensors = db.ListField()
    sids = db.ListField()
    location = db.DictField()
    cellTowers = db.DictField()
    address = db.DictField()
    meta = {
        'collection': 'pods'
    }

    def __repr__(self):
        return '<Pod %r>' % self.name

    def get_id(self):
        return unicode(self.id)

    @staticmethod
    def generate_fake(count=100):
        from random import choice, randint
        from faker import Faker

        fake = Faker()
        fake.seed(3123)
        for i in range(count):
            pod = Pod(
                name=fake.first_name() + '-' + fake.last_name() + '-' +
                str(fake.random_int(min=1000)),
                owner=fake.user_name(),
                pod_id=fake.random_int(min=20),
                qr='https://s3.amazonaws.com/pulsepodqrsvgs/default.svg',
                imei=str(randint(100000000000000, 999999999999999)),
                radio='gsm',
                last=fake.date_time_this_month(),
                voltage=randint(300, 400),
                mode=choice(['normal', 'teenager', 'asleep', 'inactive']),
                number='6096584015',
                nbk_name='Data from ' + fake.street_address(),
                sensors=[],
                sids=[randint(1, 20), randint(1, 20), randint(1, 20)],
                location={
                    'lat': float(fake.latitude()),
                    'lng': float(fake.longitude()),
                    'accuracy': randint(1, 100)
                },
                elevation={
                    'elevation': randint(10, 1000),
                    'resolution': randint(1, 10)
                },
                cellTowers={
                    'cellId': randint(10000000, 99999999),
                    'locationAreaCode': randint(10000, 99999),
                    'mobileCountryCode': randint(100, 999),
                    'mobileNetworkCode': randint(100, 999),
                    'age': randint(0, 1000)
                },
                address={
                    'formatted_address': fake.street_address(),
                    'street_address': fake.street_address(),
                    'country': fake.country(),
                    'administrative_area_level_1': fake.state(),
                    'administrative_area_level_2': fake.city(),
                },
                tags=fake.words(nb=5)
            )
            try:
                pod.save()
            except:
                "Pod save failed"


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
