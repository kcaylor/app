from . import db


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

    def reset_observations(self):
        from .data import Data
        self.observations = Data.objects(notebook=self).count()
        self.save()

    def xls(self, filename=None):
        import xlsxwriter
        from .data import Data
        from flask import current_app as app
        xlsx_path = app.config['XLSX_PATH']
        # Go get all the data for this notebook
        data = Data.objects(notebook=self.id)
        # Initalize the workbook
        if not filename:
            filename = xlsx_path + '%s.xlsx' % unicode(self.nbk_id)
        workbook = xlsxwriter.Workbook(filename)
        # Set up formatting for cells
        date_format = workbook.add_format(
            {'num_format': 'mmm d yyyy hh:mm:ss AM/PM'}
        )
        date_format.set_align('left')
        value_format = workbook.add_format(
            {'num_format': '0.00'}
        )
        value_format.set_align('center')
        average_format = workbook.add_format()
        average_format.set_align('right')
        location_format = workbook.add_format(
            {'num_format': '0.000'}
        )
        location_format.set_align('center')
        header_format = workbook.add_format()
        header_format.set_bold()
        header_format.set_align('center')
        header_format.set_align('vcenter')
        info_format = workbook.add_format()
        info_format.set_align('left')
        info_label_format = workbook.add_format()
        info_label_format.set_align('right')
        info_label_format.set_bold()
        # The first worksheet contains notebook metadata
        info_worksheet = workbook.add_worksheet('Info')
        header = '&C&"Arial Bold"%s' % self.name
        info_worksheet.set_header(header)
        info_worksheet.set_portrait()
        info_worksheet.write(0, 0, 'Notebook Name:', info_label_format)
        info_worksheet.write(0, 1, '%s' % self.name, info_format)
        info_worksheet.write(1, 0, 'Notebook Id:', info_label_format)
        info_worksheet.write(1, 1, '%s' % unicode(self.nbk_id), info_format)
        info_worksheet.write(2, 0, 'Number of Sensors:', info_label_format)
        info_worksheet.write(2, 1, len(self.sensors), info_format)
        info_worksheet.write(
            3, 0, 'Number of Observations:', info_label_format
        )
        info_worksheet.write(3, 1, self.observations, info_format)
        info_worksheet.write(4, 0, 'Last Data:', info_label_format)
        info_worksheet.write(4, 1, self.last, date_format)
        info_worksheet.write(5, 0, 'Country:', info_label_format)
        info_worksheet.write(
            5, 1, self.address['country']['full'], info_format
        )
        info_worksheet.write(6, 0, 'Address:', info_label_format)
        info_worksheet.write(
            6, 1, self.address['formatted_address'], info_format
        )
        info_worksheet.write(7, 0, 'Latitude:', info_label_format)
        info_worksheet.write(7, 1, self.lat(), info_format)
        info_worksheet.write(8, 0, 'Longitude:', info_label_format)
        info_worksheet.write(8, 1, self.lng(), info_format)
        info_worksheet.write(9, 0, 'Elevation (m):', info_label_format)
        info_worksheet.write(9, 1, self.elevation['elevation'], info_format)
        info_worksheet.write(10, 0, 'Pod:', info_label_format)
        info_worksheet.write(10, 1, self.pod.name, info_format)
        info_worksheet.set_column('A:A', 25)
        info_worksheet.set_column('B:B', 40)

        # Write the variable worksheets:
        data_worksheet = {}
        for sensor in self.sensors:
            variable = sensor.context + ' ' + sensor.variable
            data_worksheet[variable] = workbook.add_worksheet(variable)
            header = '&C&"Arial Bold"%s, %s' % (self.name, variable)
            data_worksheet[variable].set_header(header)
            data_worksheet[variable].set_portrait()
            data_worksheet[variable].repeat_rows(0, 1)
            # Add a header row to this data:
            data_worksheet[variable].set_column('A:A', 25)
            data_worksheet[variable].set_column('B:B', 12)
            data_worksheet[variable].set_column('C:C', 12)
            data_worksheet[variable].set_column('D:D', 12)
            data_header = "%s, [%s]" % (variable, sensor.unit)
            data_worksheet[variable].write(0, 0, data_header, header_format)
            data_worksheet[variable].write(1, 0, 'Time Stamp', header_format)
            data_worksheet[variable].write(1, 1, 'Latitude', header_format)
            data_worksheet[variable].write(1, 2, 'Longitude', header_format)
            value_header = 'Value (%s)' % sensor.unit
            data_worksheet[variable].write(1, 3, value_header, header_format)
            row = 2
            col = 0
            # Write the data for this variable:
            for time, variable, value in \
                    [item.display() for item in data(sensor=sensor)]:
                data_worksheet[variable].write(
                    row, col, time, date_format
                )
                data_worksheet[variable].write(
                    row, col + 1, self.lat(), location_format
                )
                data_worksheet[variable].write(
                    row, col + 2, self.lng(), location_format
                )
                data_worksheet[variable].write(
                    row, col + 3, value, value_format
                )
                row += 1
            data_worksheet[variable].write(row, 2, 'Average:', average_format)
            data_worksheet[variable].write(
                row, 3, "=AVERAGE(D1:D%d)" % int(row), value_format
            )
            data_worksheet[variable].write(
                row + 1, 2, 'Maximum:', average_format
            )
            data_worksheet[variable].write(
                row + 1, 3, "=MAX(D1:D%d)" % int(row), value_format
            )
            data_worksheet[variable].write(
                row + 2, 2, 'Minimum:', average_format
            )
            data_worksheet[variable].write(
                row + 2, 3, "=MIN(D1:D%d)" % int(row), value_format
            )

        workbook.close()

        # Put the file on Amazon...?
        # Why? Just que it and re-generate on each request...
        # Or write it to Amazon, and then re-write on each new post.
        # Or write it to the User's dropbox account if they've linked?

    @staticmethod
    def generate_fake(count=100):
        from random import choice, randint
        from faker import Faker
        from .pod import Pod
        import uuid
        fake = Faker()
        # fake.seed(3123)
        fake_notebooks = []
        nPods = Pod.objects().count()
        for i in range(count):
            try:
                if nPods > 0:
                    pod = Pod.objects()[randint(0, nPods - 1)]
                else:
                    pod = Pod.generate_fake(1)[0]
            except:
                return 'Error: No Pod objects defined'
            try:
                sensors = []
            except:
                return 'Error: No Sensor objects defined'
            notebook = Notebook(
                pod=pod,
                pod_id=pod.pod_id,
                nbk_id=uuid.uuid4(),
                owner=pod['owner'],
                confirmed=choice([True, True, True, True, False]),
                public=choice([True, True, True, False, False]),
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
                    'country': {'full': fake.country()},
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
