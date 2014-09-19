from . import Message
from flask import current_app


class DeployMessage(Message):

    def __init__(self, message=None):
        super(DeployMessage, self).__init__()
        self.type = 'deploy'
        self.frame = self.__class__.__name__
        self.format.extend([
            {'name': 'mcc', 'length': 3},
            {'name': 'mnc', 'length': 3},
            {'name': 'lac', 'length': 4},
            {'name': 'cell_id', 'length': 4},
            {'name': 'voltage', 'length': 8},
            {'name': 'n_sensors', 'length': 2},
        ])
        if message is not None:
            self.init(message=message)

    def create_fake_message(self, frame_id, notebook):
        deploy_str = self.create_fake_header(frame_id, notebook)
        import struct
        from random import random, sample
        from ..sensor import Sensor
        mcc = 310
        mnc = 26
        lac = 802
        cell_id = 10693
        n_sensors = 3
        voltage = struct.pack(
            '<f',
            float(3.6 + random() / 2)).encode('hex').zfill(
            self.get_length('voltage'))
        sensors = [Sensor.objects()[i] for i in sorted(
            sample(range(Sensor.objects().count()), n_sensors)
        )]
        deploy_str += ('%i' % int(mcc)).zfill(self.get_length('mcc'))
        deploy_str += ('%i' % int(mnc)).zfill(self.get_length('mnc'))
        deploy_str += ('%x' % int(lac)).zfill(self.get_length('lac'))
        deploy_str += ('%x' % int(cell_id)).zfill(
            self.get_length('cell_id'))
        deploy_str += voltage
        deploy_str += ('%x' % int(n_sensors)).zfill(
            self.get_length('n_sensors'))
        deploy_str += ''.join(
            [('%x' % int(x)).zfill(self.SID_LENGTH) for x in
                [str(sensor.sid) for sensor in sensors]])
        return deploy_str

    def new_nbk_id(self):
        import uuid
        # For deployment message, generate a random string:
        return str(uuid.uuid4())

    def mcc(self):
        (start, end) = self.get_position('mcc')
        if self.content:
            try:
                return int(self.content[start:end])
            except ValueError as e:
                e.args += ('message content invalid', 'DeployMessage', 'mcc()')
                raise
        else:
            self.message.status = 'invalid'
            self.message.save()
            assert 0, "Uh-oh. No message content."

    def mnc(self):
        (start, end) = self.get_position('mnc')
        if self.content:
            try:
                return int(self.content[start:end])
            except ValueError as e:
                self.message.status = 'invalid'
                self.message.save()
                e.args += ('message content invalid', 'DeployMessage', 'mnc()')
                raise
        else:
            self.message.status = 'invalid'
            self.message.save()
            assert 0, "Uh-oh. No message content."

    def lac(self):
        (start, end) = self.get_position('lac')
        if self.content:
            try:
                return int(self.content[start:end], 16)
            except ValueError as e:
                e.args += ('message content invalid', 'DeployMessage', 'lac()')
                raise
        else:
            self.message.status = 'invalid'
            self.message.save()
            assert 0, "Uh-oh. No message content."

    def cell_id(self):
        (start, end) = self.get_position('cell_id')
        if self.content:
            try:
                return int(self.content[start:end], 16)
            except ValueError as e:
                self.status = 'invalid'
                e.args += ('message content invalid',
                           'DeployMessage',
                           'cell_id()')
                raise
        else:
            self.message.status = 'invalid'
            self.message.save()
            assert 0, "Uh-oh. No message content."

    def voltage(self):
        import struct
        (start, end) = self.get_position('voltage')
        if self.content and len(self.content) >= end:
            try:
                return struct.unpack(
                    '<f',
                    self.content[start:end].decode('hex'))[0]
            except ValueError as e:
                self.message.status = 'invalid'
                self.message.save()
                e.args += ('message content invalid',
                           'DeployMessage',
                           'voltage()')
                raise
        else:
            self.message.status = 'invalid'
            self.message.save()
            assert 0, "Uh-oh. No message content."

    def n_sensors(self):
        (start, end) = self.get_position('n_sensors')
        if self.content:
            try:
                return int(self.content[start:end], 16)
            except ValueError as e:
                self.message.status = 'invalid'
                self.message.save()
                e.args += ('message content invalid',
                           'DeployMessage',
                           'n_sensors()')
                raise
        else:
            self.message.status = 'invalid'
            self.message.save()
            assert 0, "Uh-oh. No message content."

    def get_sensors(self):
        from ..sensor import Sensor
        i = self.format_length()
        sensors = []
        if len(self.content) < i:
            self.message.status = 'invalid'
            self.message.save()
            assert 0, 'message content length=' + str(len(self.content)) + \
                      '. Must be >' + str(i)
            return
        elif len(self.content) != (i + self.SID_LENGTH * self.n_sensors()):
            self.message.status = 'invalid'
            self.message.save()
            assert 0, 'message content length=' + str(len(self.content)) + \
                      '. Must equal ' + \
                      str(i + self.SID_LENGTH * self.n_sensors())
            return

        try:
            for j in range(self.n_sensors()):
                sid = int(self.content[i:i + self.SID_LENGTH], 16)
                sensor = Sensor.objects(sid=sid).first()
                sensors.append(sensor)
                i += self.SID_LENGTH
        except:
            self.message.status = 'invalid'
            self.message.save()
            assert 0, 'error reading sensor from database'
        return sensors

    def default_name(self, address):
        return str(self.pod['name']) + ' data from ' + \
            address['locality']['short'] + ', ' + \
            address['administrative_area_level_1']['short'] + \
            ' in ' + address['country']['short']

    def make_tower(self):
        return {
            'locationAreaCode': self.lac(),
            'cellId': self.cell_id(),
            'mobileNetworkCode': self.mnc(),
            'mobileCountryCode': self.mcc()
        }

    def google_geolocate_api(self):
        import json
        import requests
        towers = []
        try:
            towers.append(self.make_tower())
        except:
            self.message.status = 'invalid'
            self.message.save()
            assert 0, 'error extracting cell information from message content'
        api_key = current_app.config['GOOGLE_API_KEY']
        if not api_key:
            assert 0, "Must provide api_key"
        url = 'https://www.googleapis.com/geolocation/v1/geolocate?key=' \
            + api_key
        headers = {'content-type': 'application/json'}
        data = {'cellTowers': towers}
        response = requests.post(
            url,
            data=json.dumps(data),
            headers=headers).json()
        location = {
            'type': 'Point',
            'coordinates': [
                -9999,
                -9999
            ]
        }
        if 'error' not in response:
            location['coordinates'] = [
                response['location']['lng'],
                response['location']['lat']
            ]
            return location
        else:
            print response
            return 0

    def google_elevation_api(self, loc=None):
        import requests
        if loc is None:
            assert 0, "Must provide a location value (GeoJSON point)." + \
                      " Did you mean to call google_geolocate_api() first?"
        api_key = current_app.config['GOOGLE_API_KEY']
        if not api_key:
            assert 0, "Must provide api_key"
        if -9999 not in loc['coordinates']:
            baseurl = 'https://maps.googleapis.com/' + \
                      'maps/api/elevation/json?' + \
                      'locations='
            tailurl = '&sensor=false&key=' + api_key
            lng = str(loc['coordinates'][0])
            lat = str(loc['coordinates'][1])
            url = baseurl + lat + ',' + lng + tailurl
            response = requests.get(url).json()
            if response['status'] == 'OK':
                return {
                    'elevation': response['results'][0]['elevation'],
                    'resolution': response['results'][0]['resolution']
                }
            else:
                return 0
        else:
            return 0

    def google_geocoding_api(self, loc):
        import requests
        if loc is None:
            assert 0, "Must provide a location value (GeoJSON point)." + \
                      " Did you mean to call google_geolocate_api() first?"
        api_key = current_app.config['GOOGLE_API_KEY']
        if not api_key:
            assert 0, "Must provide api_key"
        # must pre-seed this with all the data we want shorted:
        address = {
            'country': {'short': 'unknown', 'full': 'unknown'},
            'locality': {'short': 'unknown', 'full': 'unknown'},
            'administrative_area_level_1': {
                'short': 'unknown',
                'full': 'unknown'},
            'administrative_area_level_2': {
                'short': 'unknown',
                'full': 'unknown'},
            'administrative_area_level_3': {
                'short': 'unknown',
                'full': 'unknown'},
            'route': {'short': 'unknown', 'full': 'unknown'},
            'street_address': {'short': 'unknown', 'full': 'unknown'},
        }
        if -9999 not in loc['coordinates']:
            baseurl = 'https://maps.googleapis.com/maps/' + \
                      'api/geocode/json?latlng='
            tailurl = '&sensor=false&key=' + api_key
            lng = str(loc['coordinates'][0])
            lat = str(loc['coordinates'][1])
            url = baseurl + lat + ',' + lng + tailurl
            response = requests.get(url).json()
            if response['status'] == 'OK':
                address['formatted_address'] = \
                    response['results'][0]['formatted_address']
                for result in response['results']:
                    for address_component in result['address_components']:
                        if address_component['types'][0] in address and \
                                'short' in \
                                address[address_component['types'][0]]:
                            address[address_component['types'][0]]['full'] = \
                                str(address_component['long_name'])
                            address[address_component['types'][0]]['short'] = \
                                str(address_component['short_name'])
                        else:
                            address[address_component['types'][0]] = \
                                str(address_component['long_name'])
        return address

    def create_alert(self, notebook):
        alert1 = 'Hi %s! ' % notebook.owner['username']
        alert1 += 'You just deployed your pod, %s, near %s in %s, %s.' % (
            notebook.pod['name'],
            notebook.address['formatted_address'],
            notebook.address['administrative_area_level_1'],
            notebook.address['country']['full']
        )
        link = 'https://app.pulsepod.io/notebooks/%s' % notebook.get_id()
        alert2 = ' Data from this pod will now be recorded at %s.' % link
        return (alert1, alert2)

    def parse(self):
        from ..notebook import Notebook
        from ..pod import Pod
        from ..user import User
        import datetime
        if self.status is not 'invalid':
            if self.status not in ['parsed', 'posted']:
                try:
                    location = self.google_geolocate_api()
                    elevation = self.google_elevation_api(location)
                    address = self.google_geocoding_api(location)
                except:
                    self.message.status = 'invalid'
                    self.message.save()
                    assert 0, 'MessageParse: Error in Google API functions'
                try:
                    notebook = Notebook(
                        pod_id=self.pod['pod_id'],
                        pod=self.pod,
                        sensors=self.get_sensors(),
                        sids=[sensor.sid for sensor in self.get_sensors()],
                        owner=self.pod['owner'],
                        last=datetime.datetime.utcnow(),
                        voltage=self.voltage(),
                        location=location,
                        elevation=elevation,
                        address=address,
                        name=self.default_name(address),
                        nbk_id=self.new_nbk_id(),
                        created_at=datetime.datetime.utcnow(),
                        confirmed=False
                    )
                    self.message.status = 'parsed'
                    self.message.save()
                except:
                    assert 0, 'MessageParse: Error creating new notebook'
                    self.message.status = 'invalid'
                    self.message.save()
                try:
                    notebook.save()
                    Pod.objects(id=self.pod.id).update_one(
                        inc__notebooks=1,
                        set__current_notebook=notebook,
                        set__number=self.number
                    )
                    User.objects(id=self.pod.owner.id).update_one(
                        inc__notebooks=1
                    )
                    self.message.status = 'posted'
                    self.message.save()
                    print "Added notebook %s to the database" % \
                        notebook.__repr__()
                    print "Incremented notebooks for %s and %s" % \
                        (self.pod.__repr__(), self.pod.owner.__repr__())
                    print "Changed current notebook on %s to %s" % \
                        (self.pod.__repr__(), notebook.__repr__())
                except:
                    assert 0, 'MessageParse: Error saving new notebook'
                if notebook.owner.phone_number:
                    alerts = self.create_alert(notebook)
                    for alert in alerts:
                        self.message.send_message(
                            number=notebook.owner.phone_number,
                            content=alert
                        )
                elif 'email' in dir(notebook.owner):
                    print 'sending deploy alert email [NOT FUNCTIONAL]'
                else:
                    print "no user data available"
            else:
                return "message already parsed"

    def post(self):
        pass


class DeployMessageLong(DeployMessage):

    def __init__(self, message=None):
        super(DeployMessageLong, self).__init__()
        self.type = 'deploy_long'
        self.frame = self.__class__.__name__
        # Modify the format:
        (item for item in self.format if item["name"] == 'cell_id').next(
            )['length'] = 8
        (item for item in self.format if item["name"] == 'lac').next(
            )['length'] = 8
