from . import Message


class StatusMessage(Message):

    def __init__(self, message=None):
        super(StatusMessage, self).__init__()
        self.type = 'status'
        self.frame = self.__class__.__name__
        if message is not None:
            self.init(message=message)

    def create_fake_message(self, frame_id, notebook):
        message_str = self.create_fake_header(frame_id, notebook)
        return message_str

    def parse(self):
        pass

    def post(self):
        pass
