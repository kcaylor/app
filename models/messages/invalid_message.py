from . import Message


class InvalidMessage(Message):

    def __init__(self, message=None):
        super(InvalidMessage, self).__init__()
        self.status = 'invalid'
        self.type = 'invalid'
        self.frame = self.__class__.__name__
        if message is not None:
            self.init(message=message)

    def create_fake_message(self, frame_id, notebook):
        return 'this is a fake message'

    def parse(self):
        self.message.save()


class UnknownMessage(InvalidMessage):

    def __init__(self, message=None):
        super(UnknownMessage, self).__init__()
        self.status = 'unknown'
        self.type = 'unknown'
        self.frame = self.__class__.__name__
        if message is not None:
            self.init(message=message)
