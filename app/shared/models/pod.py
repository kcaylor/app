from . import db
import datetime
from flask import current_app


class Pod(db.Document):

    MODES = ['inactive', 'teenager', 'asleep', 'normal']
    RADIOS = ['gsm', 'cdma', 'wcdma', 'wifi', 'irridium']

    name = db.StringField()
    created = db.DateTimeField(default=datetime.datetime.now())
    updated = db.DateTimeField(default=datetime.datetime.now())
    owner = db.ReferenceField('User')
    pod_id = db.IntField()
    qr = db.StringField(
        default='https://s3.amazonaws.com/pulsepodqrsvgs/default.svg'
    )
    imei = db.StringField(
        default='000000000000000'
    )
    radio = db.StringField(
        choices=RADIOS,
        default='gsm'
    )
    mode = db.StringField(
        choices=MODES,
        default='asleep'
    )
    number = db.StringField(
        default='18005551212'
    )
    last = db.DateTimeField(
        default=datetime.datetime.now())
    current_notebook = db.ReferenceField('Notebook')
    notebooks = db.IntField(
        default=0
    )
    observations = db.IntField(
        default=0
    )
    about = db.StringField(
        default='No additional information available for this pod'
    )
    # updated = db.DateTimeField()
    # created = db.DateTimeField()
    meta = {
        'collection': 'pods',
        'indexes': [
            'name', 'pod_id', 'number', 'mode', 'owner'],
        'index_background': True,
        'ordering': ['-last'],
    }

    def __repr__(self):
        return '<Pod %r>' % self.name

    def get_id(self):
        return unicode(self.id)

    @staticmethod
    def generate_fake(count=100):
        from random import choice, randint
        from faker import Faker
        from .user import User
        import phonenumbers
        nusers = User.objects().count()
        fake = Faker()
        # fake.seed(3123)
        fake_pods = []
        for i in range(count):
            if nusers > 0:
                user = User.objects()[randint(0, nusers - 1)]
            else:
                user = User.generate_fake(1)[0]
            pod = Pod(
                name=fake.first_name() + '-' + fake.last_name() + '-' +
                str(fake.random_int(min=1000)),
                owner=user,
                pod_id=fake.random_int(min=20),
                qr='https://s3.amazonaws.com/pulsepodqrsvgs/default.svg',
                imei=str(randint(100000000000000, 999999999999999)),
                radio='gsm',
                mode=choice(['normal', 'teenager', 'asleep', 'inactive']),
                number=phonenumbers.format_number(
                    phonenumbers.parse(
                        '1' + ''.join([str(randint(0, 9)) for x in range(7)]),
                        'US'),
                    phonenumbers.PhoneNumberFormat.E164),
            )
            try:
                pod.save()
                fake_pods.append(pod)
            except:
                "Pod save failed"
        return fake_pods

    def create_qr(self):
        raise NotImplementedError
