from flask.ext.login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from datetime import datetime


def make_api_key():
    import uuid
    return str(uuid.uuid4()).replace('-', '')


def make_api_key():
    import uuid
    return str(uuid.uuid4()).replace('-', '')


class User(UserMixin, db.Document):

    ROLES = ['admin', 'user', 'guest']

    confirmed = db.BooleanField(default=False)
    username = db.StringField(max_length=64, unique=True)
    email = db.StringField(max_length=64, unique=True)
    password_hash = db.StringField(max_length=120)
    last_seen = db.DateTimeField()
    member_since = db.DateTimeField(default=datetime.utcnow())
    notebooks = db.IntField(
        default=0
    )
    pods = db.IntField(
        default=0
    )
    observations = db.IntField(
        default=0
    )
    api_key = db.StringField(
        max_length=64,
        unique=True,
        default=make_api_key()
    )
    role = db.StringField(
        choices=ROLES,
        default='user')

    phone_number = db.StringField()

    meta = {
        'indexes': ['email', 'username', 'api_key'],
        'collection': 'users',
    }

    def can_edit(self, notebook):
        if self.role == 'admin':
            return True
        if self.role == 'guest':
            return False
        if self.role == 'user':
            try:
                owner = notebook.owner.username
                return owner == self.username
            except AttributeError:
                return False
        return False

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.get_id()})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.get_id():
            return False
        self.password = new_password
        self.save()
        return True

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.get_id()})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.get_id():
            return False
        self.confirmed = True
        self.save()
        return True

    def ping(self):
        self.last_seen = datetime.utcnow()
        self.save()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        if password:
            self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username

    def __unicode__(self):
        return self.id

    def get_id(self):
        return unicode(self.id)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_administrator(self):
        if self.role == 'admin':
            return True
        else:
            return False

    def is_anonymous(self):
        return False

    @staticmethod
    def verify_api_key(api_key):
        return User.objects(api_key=api_key).first()

    @staticmethod
    def create_administrator():
        if User.objects(role='admin').count() > 0:
            return "Administrator already exists"
        import os
        admin = User(
            confirmed=True,
            username=os.environ.get('ADMIN_USER'),
            email=os.environ.get('ADMIN_EMAIL'),
            role='admin',
            api_key=os.environ.get('ADMIN_API_KEY')
        )
        admin.password = os.environ.get('ADMIN_PASSWORD')
        admin.save()

    @staticmethod
    def create_guest():
        if User.objects(role='guest').count() > 0:
            return "Guest user already exists"
        guest = User(
            confirmed=True,
            username='guest',
            email='guest@pulsepod.io',
            role='guest',
            api_key=make_api_key()
        )
        guest.password = 'pulsepodguest'
        guest.save()

    @staticmethod
    def generate_fake(count=10):
        from faker import Faker
        fake = Faker()
        # fake.seed(3123)
        fake_users = []
        for i in range(count):
            user = User(
                confirmed=True,
                username=fake.user_name(),
                email=fake.safe_email(),
                api_key=make_api_key()
            )
            #try:
            user.password = fake.md5()
            user.save()
            fake_users.append(user)
            #except:
            #    print "Unable to save user"
        return fake_users


class AnonymousUser(AnonymousUserMixin):

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

    def get_id(self):
        return None

    def can_edit(self, notebook):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    user = User.objects.with_id(user_id)
    return user
