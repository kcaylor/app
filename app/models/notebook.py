from .. import db


class Notebook(db.Document):

    name = db.StringField(db_field='name')
    pod_id = db.IntField(
        required=True,
        db_field='pod_id')
    nbk_id = db.UUIDField(
        required=True,
        unique=True
    )
    pod = db.ReferenceField('Pod')
    elevation = db.DictField()
    sensors = db.ListField(
        db.ReferenceField('Sensor')
    )
    shared = db.ListField(
        db.ReferenceField('User'),
        default=[]
    )
    public = db.BooleanField(default=True)
    confirmed = db.BooleanField(default=False)
    owner = db.ReferenceField('User')
    sids = db.ListField(db.IntField())
    location = db.PointField()
    cellTower = db.DictField()
    address = db.DictField()
    last = db.DateTimeField()
    voltage = db.FloatField(default=3.8)
    confirmed = db.BooleanField(default=False)
    observations = db.IntField(
        default=0
    )
    tags = db.ListField(db.StringField())

    meta = {
        'collection': 'notebooks',
        'index_background': True,
        'indexes': [
            'owner',
            ('owner', '-last'),
            'pod'
        ]
    }

    def __repr__(self):
        return '<Notebook %r>' % self.name

    def get_id(self):
        return unicode(self.id)

    def lat(self):
        return self.location['coordinates'][1]

    def lng(self):
        return self.location['coordinates'][0]

    def map_coords(self):
        return [self.location['coordinates'][1],
                self.location['coordinates'][0]]

    @staticmethod
    def generate_fake(count=100):
        from random import choice, randint, sample
        from faker import Faker
        from .pod import Pod
        from .sensor import Sensor
        import uuid
        fake = Faker()
        # fake.seed(3123)
        fake_notebooks = []
        nPods = Pod.objects().count()
        nSensors = Sensor.objects().count()
        for i in range(count):
            try:
                if nPods > 0:
                    pod = Pod.objects()[randint(0, nPods-1)]
                else:
                    pod = Pod.generate_fake(1)[0]
            except:
                return 'Error: No Pod objects defined'
            try:
                if nSensors >= 3:
                    sensors = [Sensor.objects()[i] for i in sorted(
                        sample(range(nSensors), 3)
                    )]
                else:
                    sensors = Sensor.generate_fake(3)
            except:
                return 'Error: No Sensor objects defined'
            notebook = Notebook(
                pod=pod,
                pod_id=pod.pod_id,
                nbk_id=uuid.uuid4(),
                owner=pod['owner'],
                last=fake.date_time_this_month(),
                name='Data from ' + fake.street_address(),
                sensors=sensors,
                sids=[sensors[x].sid for x in range(len(sensors))],
                # Note: Need to update the google location function to return
                # a valid GeoJSON object...
                location={'type': 'Point',
                          'coordinates': [
                              float(fake.longitude()),
                              float(fake.latitude())]},
                elevation={
                    'elevation': randint(10, 1000),
                    'resolution': randint(1, 10)
                },
                cellTower={
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
                notebook.save()
                pod['current_notebook'] = notebook
                pod.save()
                fake_notebooks.append(notebook)
            except:
                return "Notebook save failed"
        return fake_notebooks
