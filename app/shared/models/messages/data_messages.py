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
            data_str += ('%x' % int(sensor.sid)).zfill(self.SID_LENGTH)
            nobs = randint(1, 3)
            data_str += ('%x' % nobs).zfill(self.NOBS_LENGTH)
            for i in range(nobs):
                if len(data_str) < 164 - (8 + 2 * sensor.nbytes):
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
        from ..sensor import Sensor
        from ..data import Data
        from ..notebook import Notebook
        from ..pod import Pod
        from ..user import User
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
            if self.status not in ['parsed', 'posted']:
                self.status = 'parsed'
                data_list = []
                self.total_nobs = 0  # Initialize observation counter
                while i < len(self.content):
                    try:
                        sensor = self.get_sensor(i)
                    except:
                        self.message.status = 'invalid'
                        self.message.save()
                        print 'error reading sensor'
                        return
                    i += self.SID_LENGTH
                    try:
                        nobs = self.get_nobs(i)
                    except:
                        self.message.status = 'invalid'
                        self.message.save()
                        print 'error reading nobs'
                        return
                    i += self.NOBS_LENGTH
                    self.total_nobs += nobs
                    Sensor.objects(id=sensor.id).update_one(
                        inc__observations=nobs
                    )
                    print "Added %d observations to %s" % \
                        (nobs, sensor.__repr__())
                    try:
                        if sensor['context'] == '':
                            variable_name = str(sensor['variable'])
                        else:
                            variable_name = str(sensor['context']) + ' ' + \
                                str(sensor['variable'])

                    except:
                        self.message.status = 'invalid'
                        self.message.save()
                        print 'error reading variable name'
                        return

                    while nobs > 0:
                        try:
                            time_stamp = self.get_time(i)  # Get timestamp
                        except:
                            self.message.status = 'invalid'
                            self.message.save()
                            print 'error reading timestamp'
                            return
                        i += self.TIME_LENGTH
                        try:
                            value = self.get_value(i, sensor)
                        except:
                            print 'error reading value'
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
                        data_list.append(data)
                        nobs -= 1
                # Update the voltage (if we have a new value):
                voltage = self.notebook.voltage
                for data_item in data_list:
                    if data_item.sensor.name is 'vbatt':
                        voltage = data_item.value
                    # save the data, while we are here:
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
                # Update notebooks, pods, and user:
                Notebook.objects(id=self.notebook.id).update_one(
                    inc__observations=self.total_nobs,
                    set__last=nbk_last,
                    set__voltage=voltage
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
                [data_item.save() for data_item in data_list]
                for data_item in data_list:
                    print "Added %s from %s with %s" % \
                        (data_item.__repr__(),
                         data_item.sensor.__repr__(),
                         self.notebook.__repr__())
                print "Incremented %s, %s, and %s with %d observations" % \
                    (self.pod.__repr__(),
                     self.notebook.__repr__(),
                     self.notebook.owner.__repr__(),
                     self.total_nobs)
            else:
                return "message already parsed"

    def patch(self):
        pass
