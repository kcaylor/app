from flask.ext.mongoengine import MongoEngine
from flask.ext.login import LoginManager

db = MongoEngine()
login_manager = LoginManager()

# WARNING: THE EVE API EXPECTS (AND PROVIDES) DB_FIELD NAMES
# WHEN MONGOENGINE FIELD NAMES DIFFER FROM DB_FIELDS, THE API WILL
# ALWAYS USE DB_FIELD NAMES. DO NOT EXPECT DIFFERENT BEHAVIOR
# THIS IS A KNOWN ISSUE.

from .data import Data
from .message import Message
from .notebook import Notebook
from .pod import Pod
from .user import User
from .sensor import Sensor
