from . import db
import datetime


class Data(db.Document):

    time_stamp = db.DateTimeField(
        db_field='t',
        default=datetime.datetime.now())
    value = db.FloatField(
        db_field='v',
        default=None)
    location = db.PointField(db_field='loc')
    # Define links to Pod, Notebook, and Sensor collections:
    notebook = db.ReferenceField('Notebook', db_field='nbk')
    pod = db.ReferenceField('Pod', db_field='pod')
    sensor = db.ReferenceField('Sensor', db_field='s')
    variable = db.StringField()
    pod_name = db.StringField(db_field='p')
    owner = db.ReferenceField('User', db_field='owner')
    public = db.BooleanField(default=True)

    meta = {
        'collection': 'data',
        'ordering': ['-time_stamp'],
        'index_background': True,
        'indexes': [
            'notebook',
            'owner',
            ('notebook', 'sensor'),
            'location',
            ('location', '-time_stamp'),
            'pod',
            'sensor',
        ]
    }

    def __repr__(self):
        return '<Data %r>' % self.value

    def get_id(self):
        return unicode(self.id)

    def display(self):
        return [self.time_stamp, self.variable, self.value]

    def authenticate(self, user):
        if user.role == 'admin':
            return True
        elif self.notebook.owner == user:
            return True
        else:
            return False

    @staticmethod
    def generate_fake(count=1000):
        from faker import Faker
        from random import random, randint
        from .notebook import Notebook
        from .sensor import Sensor

        fake = Faker()
        # fake.seed(3123)
        fake_data = []
        nSensors = Sensor.objects().count()
        nNotebooks = Notebook.objects().count()
        if nSensors is 0:
            return "Error: No Sensor objects defined." \
                " Use Sensor.generate_fake()"
        if nNotebooks is 0:
            return "Error: No Notebook objects defined." \
                " Use Notebook.generate_fake()"
        for i in range(count):
            try:
                sensor = Sensor.objects()[
                    randint(0, nSensors - 1)
                ]
            except:
                return "Error: No Sensor objects defined"
            try:
                notebook = Notebook.objects()[
                    randint(0, nNotebooks - 1)
                ]
            except:
                return "Error: No Notebook objects defined."
            data = Data(
                time_stamp=fake.date_time_this_month(),
                location=notebook.location,
                # Sensor and pod names are fixed.
                variable=str(sensor.context) + ' ' + str(sensor.variable),
                value=random() * 100,
                pod=notebook.pod,
                sensor=sensor,
                notebook=notebook,
                owner=notebook.owner,
                public=notebook.public
            )
            try:
                data.save()
                notebook.observations += 1
                if data.sensor not in notebook.sensors:
                    notebook.sensors += data.sensor
                    notebook.sids += data.sensor.sid
                notebook.save()
                sensor.observations += 1
                sensor.save()
                notebook.owner.observations += 1
                notebook.owner.save()
                fake_data.append(data)
            except:
                "Data save failed"
        return fake_data
