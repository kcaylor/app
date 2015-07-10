from . import Message


class DataMessage(Message):

    def __init__(self, message=None):
        super(DataMessage, self).__init__()
        self.type = 'data'
        self.frame = self.__class__.__name__
        if message is not None:
            self.init(message=message)

    def create_fake_message(self, frame_id, notebook):
        data_str = self.create_fake_header(frame_id, notebook)
        from random import randint, random
        from time import time
        import struct
        now = int(time())
        hr = 60 * 60
        for sensor in notebook.sensors:
            nobs = randint(1, 3)
            len_needed = self.SID_LENGTH + self.NOBS_LENGTH + nobs * (
                8 + 2 * sensor.nbytes)
            if len(data_str) + len_needed < 164:
                data_str += ('%x' % int(sensor.sid)).zfill(self.SID_LENGTH)
                data_str += ('%x' % nobs).zfill(self.NOBS_LENGTH)
                for i in range(nobs):
                    data_str += struct.pack('<L', int(
                        now - i * hr)).encode('hex')
                    data_str += struct.pack(
                        str(sensor.byteorder + sensor.fmt),
                        random() * 100).encode('hex')
        return data_str

    def get_sensor(self, i):
        from ..sensor import Sensor
        try:
            sid = self.get_sid(i)
        except:
            print 'error reading sid'
            self.message.status = 'invalid'
            self.message.save()
            return
        try:
            sensor = Sensor.objects(sid=sid).first()
        except:
            print 'error reading sensor from database'
            self.message.status = 'invalid'
            self.message.save()
            return
        return sensor

    def parse(self):
        from ..data import Data
        """
        go through the user data of the message
        | sid | nObs | unixtime1 | value1 | unixtime2 | value2 | ... | valueN |
        sid = 1byte
        nObs = 1byte
        unixtime = 4 bytes LITTLE ENDIAN
        value = look up length
        """
        if self.status is not 'invalid':
            i = self.HEADER_LENGTH
            self.status = 'parsed'
            data_list = []
            sensor_list = []
            nobs_dict = {}
            self.total_nobs = 0  # Initialize observation counter
            while i < len(self.content):
                try:
                    sensor = self.get_sensor(i)
                    sensor_list.append(sensor)
                except:
                    self.message.status = 'invalid'
                    self.message.save()
                    print 'error reading sensor, i=%d' % i
                    return
                i += self.SID_LENGTH
                try:
                    nobs = self.get_nobs(i)
                except:
                    self.message.status = 'invalid'
                    self.message.save()
                    print 'error reading nobs, i=%d' % i
                    return
                i += self.NOBS_LENGTH
                self.total_nobs += nobs
                nobs_dict[sensor.id] = nobs
                try:
                    if sensor['context'] == '':
                        variable_name = str(sensor['variable'])
                    else:
                        variable_name = str(sensor['context']) + ' ' + \
                            str(sensor['variable'])

                except:
                    self.message.status = 'invalid'
                    self.message.save()
                    print 'error reading variable name, i=%d' % i
                    return

                while nobs > 0:
                    try:
                        # Using datetime now, so call get_datetime.
                        # time_stamp = self.get_time(i)  # Get timestamp
                        time_stamp = self.get_datetime(i)
                    except:
                        self.message.status = 'invalid'
                        self.message.save()
                        print 'error reading timestamp, i=%d' % i
                        return
                    i += self.TIME_LENGTH
                    try:
                        value = self.get_value(i, sensor)
                    except:
                        print 'error reading value, i=%d' % i
                        self.message.status = 'invalid'
                        self.message.save()
                        return

                    i += 2 * sensor['nbytes']
                    data = Data(
                        pod=self.pod,
                        notebook=self.notebook,
                        sensor=sensor,
                        value=value,
                        time_stamp=time_stamp,
                        location=self.notebook.location,
                        variable=variable_name
                    )
                    # TODO: test the time stamp here before adding to
                    # the data list. That way we keep good stuff and
                    # only throw out bad.
                    data_list.append(data)
                    nobs -= 1
            self.data_list = data_list
            self.sensor_list = sensor_list
            self.nobs_dict = nobs_dict

    def slack(self):
        from app import mqtt_q, slack
        # from ..notebook import Notebook
        # from ..sensor import Sensor
        # from ..pod import Pod
        # from ..user import User
        msg = ''
        msg += 'New data recieved for _{notebook}_\n\n'.format(
            notebook=self.notebook.name)
        # for data in self.data_list:
        #     msg += "*{context} {sensor}* was {value} at {time}\n".format(
        #         context=data.sensor.context,
        #         sensor=data.sensor.variable,
        #         value=data.value,
        #         time=data.time_stamp
        #     )
        # msg += "\nIncremented observations to "
        msg += "_{pod}_, _{notebook}_, and _{owner}_ by {nobs}\n".format(
            pod=self.pod.name,
            notebook=self.notebook.name,
            owner=self.notebook.owner.username,
            nobs=self.total_nobs)
        mqtt_q.enqueue(
            slack.chat.post_message,
            "#api",
            msg,
            username='api.pulsepod',
            icon_emoji=':rabbit:'
        )

    def post(self):
        from ..notebook import Notebook
        from ..sensor import Sensor
        from ..pod import Pod
        from ..user import User
        # Update the voltage (if we have a new value):
        voltage = self.notebook.voltage
        for data_item in self.data_list:
            if data_item.sensor.name is 'vbatt':
                voltage = data_item.value
        # Update notebook "last" time, if this message is new:
        if self.message.time_stamp > self.notebook.last:
            nbk_last = self.message.time_stamp
        else:
            nbk_last = self.notebook.last
        # Update pod "last" time, if this message is new:
        if self.message.time_stamp > self.pod.last:
            pod_last = self.message.time_stamp
        else:
            pod_last = self.pod.last
        # Increment nobs for sensors
        for sensor in self.sensor_list:
            nobs = self.nobs_dict[sensor.id]
            Sensor.objects(id=sensor.id).update_one(
                inc__observations=nobs
            )
        # Update notebooks, pods, and user:
        Notebook.objects(id=self.notebook.id).update_one(
            inc__observations=self.total_nobs,
            set__last=nbk_last,
            set__voltage=voltage,
            add_to_set__sensors=self.sensor_list,
            add_to_set__sids=[sensor.sid for sensor in self.sensor_list]
        )
        Pod.objects(id=self.pod.id).update_one(
            inc__observations=self.total_nobs,
            set__number=self.number,
            set__last=pod_last
        )
        User.objects(id=self.notebook.owner.id).update_one(
            inc__observations=self.total_nobs
        )
        self.message.status = 'posted'
        self.message.save()
        [data_item.save() for data_item in self.data_list]

    def patch(self):
        pass
