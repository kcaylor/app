import time
import struct
from ...utils import InvalidMessageException


class Message(object):

    def __init__(self, message=None):

        if message is not None:
            self.message = message

        self.format = [
            {'name': 'frame_id', 'length': 2},
            {'name': 'pod_id', 'length': 4}
        ]

        self.SID_LENGTH = 2
        self.NOBS_LENGTH = 2
        self.HEADER_LENGTH = self.get_header_length()
        self.TIME_LENGTH = 8

    def init(self, message=None):
        if message is None:
            assert 0, "Must provide a message to init()"
        self.message = message
        self.status = self.message.status
        self.type = self.message.message_type
        self.number = self.message.number

        # New things we will need to determine:
        if self.message.pod is None:
            from ..pod import Pod
            if self.message.pod_id():
                pod = Pod.objects(
                    pod_id=self.message.pod_id()).first()
                if pod:
                    self.message.pod = pod
                    self.message.save()
            else:
                self.message.status = 'invalid'
                self.status = 'invalid'
                self.message.save()
        if self.message.notebook is None and self.message.pod is not None:
            from ..notebook import Notebook
            self.message.notebook = Notebook.objects(
                id=self.message.pod.current_notebook.id).first()
            try:
                self.message.save()
            except:
                return "Unable to update message notebook"

        if self.status is not 'invalid':
            self.content = self.message.message_content
            self.pod = self.message.pod
            self.notebook = self.message.notebook

    # These functions need to be defined in each of the message
    # subclasses:
    def post(self):
        raise NotImplementedError

    def parse(self):
        raise NotImplementedError

    def slack(self):
        raise NotImplementedError

    def mqtt(self, content):
        raise NotImplementedError

    def create_fake_message(*args, **kwargs):
        raise NotImplementedError

    def emoji(self):
        raise NotImplementedError

    def create_fake_header(self, frame_id, notebook):
        header_str = ''
        header_str += ('%x' % int(frame_id)).zfill(2)
        header_str += ('%x' % int(notebook.pod.pod_id)).zfill(4)
        return header_str

    def get_length(self, value):
        seq = self.format
        try:
            return (item for item in seq if item["name"] == value).next(
                )['length']
        except StopIteration:
            raise StopIteration("%s not found in format" % value)

    def get_header_length(self):
        return (self.get_length('frame_id') + self.get_length('pod_id'))

    def get_position(self, value):
        seq = self.format
        attr = 'name'
        try:
            loc = next(index for (index, d)
                       in enumerate(seq) if d[attr] == value)
        except:
            raise
        start = 0
        for i in range(0, loc):
            try:
                start += self.format[i]['length']
            except:
                raise
            try:
                length = self.get_length(value)
            except:
                raise
            end = start + length
        return (start, end)

    def format_length(self):
        length = 0
        for item in self.format:
            length += item['length']
        return length

    def get_items(self):
        return [item['name'] for item in self.format]

    def get_sid(self, i):
        return int(self.content[i:i + self.SID_LENGTH], 16)

    def get_nobs(self, i):
        return int(self.content[i:i + self.NOBS_LENGTH], 16)

    # Pod and Notebook Ids:
    def pod_id(self):
        (start, end) = self.get_position('pod_id')
        try:
            pod_id = int(self.content[start:end], 16)
        except ValueError:
            self.message.status = 'invalid'
            self.message.save()
            assert 0, "Invalid Message: " + self.content
        return pod_id

    def get_now(self):
        return time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())

    def get_time(self, i):
        # parse unixtime to long int, then convert to database time
        try:
            unixtime = struct.unpack(
                '<L',
                self.content[i:i + self.TIME_LENGTH].decode('hex'))[0]
        except:
            raise InvalidMessageException(
                'Error decoding timestamp',
                status_code=400)
        t = time.gmtime(unixtime)
        # dbtime is (e.g.) "Tue, 17 Sep 2013 01:33:56 GMT"
        return time.strftime("%a, %d %b %Y %H:%M:%S GMT", t)

    def get_value(self, i, sensor):
        import struct
        # parse value based on format string
        try:
            value = struct.unpack(
                str(sensor['byteorder'] + sensor['fmt']),
                self.content[i:i + (2 * int(sensor['nbytes']))].decode('hex'))[0]
        except:
            raise InvalidMessageException(
                'Error parsing format string',
                status_code=400)

        # Right here we would do some initial QA/QC based on whatever
        # QA/QC limits we eventually add to the sensor specifications.
        # Not returning the flag yet.
        self.qa_qc(sensor, value)
        return float(value)

    def qa_qc(self, sensor, value):
        pass

