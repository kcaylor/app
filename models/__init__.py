from flask.ext.mongoengine import MongoEngine
from flask.ext.login import LoginManager

db = MongoEngine()
login_manager = LoginManager()


from .data import Data
from .message import Message
from .notebook import Notebook
from .pod import Pod
from .user import User
from .sensor import Sensor
