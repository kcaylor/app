from . import db
from flask import current_app
import datetime
from messages.invalid_message import InvalidMessage, UnknownMessage
from messages.status_message import StatusMessage
from messages.data_messages import DataMessage
from messages.deploy_messages import DeployMessage, DeployMessageLong


class NewMessageObject(object):
    @staticmethod
    def create(message_type=None):
        if message_type is None:
            assert 0, "Must provide a message_type"
        if message_type == "data":
            return DataMessage()
        if message_type == "status":
            return StatusMessage()
        if message_type == "deploy":
                return DeployMessage()
        if message_type == "deploy_long":
                return DeployMessageLong()
        if message_type == "invalid":
            return InvalidMessage()
        return UnknownMessage()


class Message(db.Document):

    STATUS = ['queued', 'parsed', 'posted', 'unknown', 'invalid']
    SOURCES = ['smssync', 'twilio', 'nexmo', 'pulsepi', 'unknown']

    FRAMES = {
        1: 'status',
        2: 'data',
        3: 'deploy',
        4: 'deploy_long',
    }

    message_content = db.StringField(
        max_length=170,
        default=None,
        required=True,
        db_field='message',
    )
    status = db.StringField(
        choices=STATUS,
        default='queued'
    )
    message_id = db.StringField(
        max_length=40,
        db_field='mid',
        required=True,
        unique=True
    )
    number = db.StringField(
        max_length=20,
        default='+18888675309')
    time_stamp = db.DateTimeField(
        default=datetime.datetime.now
    )
    source = db.StringField(
        choices=SOURCES,
        required=True
    )
    message_type = db.StringField(
        choices=FRAMES.values()+list(['unknown', 'invalid']),
        db_field='type',
        default='unknown'
    )
    frame_id = db.IntField(
        choices=FRAMES.keys(),
        db_field='frame_id',
        default=None
    )
    pod = db.ReferenceField('Pod')
    notebook = db.ReferenceField('Notebook')

    meta = {
        'indexes': [
            'source', 'status', 'message_type', 'pod', 'notebook'],
        'index_background': True,
        'ordering': ['-time_stamp'],
        'collection': 'messages',
        'allow_inheritance': True
    }

    @staticmethod
    def generate_fake(count=1, frame_id=None):
        from random import choice, randint, sample
        from faker import Faker
        from .notebook import Notebook
        fake = Faker()
        # fake.seed(3123)
        fake_messages = []
        nNotebooks = Notebook.objects().count()
        for i in range(count):
            try:
                if nNotebooks > 0:
                    notebook = Notebook.objects()[randint(
                        0, nNotebooks-1)]
                else:
                    notebook = Notebook.generate_fake(1)[0]
            except:
                return 'Error: No Notebook objects defined'
            if frame_id is None:
                frame = choice(Message.FRAMES.keys())
            else:
                frame = frame_id
            Obj = NewMessageObject.create(Message.FRAMES[frame])
            message_str = Obj.create_fake_message(frame, notebook)
            message = Message(
                message_id=str(fake.random_int(min=100000, max=100000000)),
                number=notebook.pod.number,
                source=choice(Message.SOURCES),
                message=message_str,
                pod=notebook.pod,
                notebook=notebook)
            # try:
            message.message_type = message.get_type()
            message.frame_id = message.get_frame_id()
            message.save()
            fake_messages.append(message)
        # except:
        #        return "Unable to save message"
        return fake_messages

    def __repr__(self):
        return '<Message %r>' % self.message_content

    def __unicode__(self):
        return self.id

    def get_frame_id(self):
        try:
            return int(self.message_content[0:2], 16)
        except ValueError:
            return 9999

    def get_type(self):
        try:
            return Message.FRAMES[self.get_frame_id()]
        except KeyError:
            return 'invalid'

    def pod_id(self):
        try:
            return int(self.message_content[2:6], 16)
        except ValueError:
            self.status = 'invalid'
            self.save()
            return None

    def get_id(self):
        return unicode(self.id)

    def get_time(self):
        return self.time_stamp.strftime("%a, %d %b %Y %H:%M:%S GMT")

    def compute_signature(self):
        from app.HMACAuth import compute_signature
        from requests.auth import HTTPBasicAuth
        import json
        data = {}
        data['message'] = self.message_content
        data['time_stamp'] = self.get_time()
        data['source'] = self.source
        data['number'] = self.number
        data['mid'] = self.message_id
        user = 'gateway'
        url = current_app.config['API_URL'] + '/messages/' + self.source
        print url
        return compute_signature(
            current_app.config['API_AUTH_TOKEN'],
            url,
            json.dumps(data))

    def get_data(self):
        data = {}
        data['message'] = self.message_content
        data['time_stamp'] = self.get_time()
        data['source'] = self.source
        data['number'] = self.number
        data['mid'] = self.message_id
        return data

    def init(self):
        MessageObject = NewMessageObject.create(self.get_type())
        MessageObject.init(self)
        self.parse = MessageObject.parse
        self.Message = MessageObject


class TwilioMessage(Message):

    def __repr__(self):
        return '<TwilioMessage %r>' % self.message_content


class PulsePiMessage(Message):

    def __repr__(self):
        return '<PulsePiMessage %r>' % self.message_content
