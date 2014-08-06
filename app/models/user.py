from flask.ext.login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
import datetime


class User(UserMixin, db.Document):

    confirmed = db.BooleanField(default=False)
    username = db.StringField(max_length=64, unique=True)
    email = db.StringField(max_length=64, unique=True)
    password_hash = db.StringField(max_length=120)
    notebooks = db.IntField(
        default=0
    )
    observations = db.IntField(
        default=0
    )
    role = db.StringField(default='user')
    meta = {
        'indexes': ['email', 'username'],
        'collection': 'users',
    }

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

    @staticmethod
    def generate_fake(count=10):
        from random import choice, randint, sample
        from faker import Faker
        fake = Faker()
        # fake.seed(3123)
        fake_users = []
        for i in range(count):
            user = User(
                confirmed=True,
                username=fake.user_name(),
                email=fake.safe_email(),
                password=fake.md5()
            )
            #try:
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

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    user = User.objects.with_id(user_id)
    return user
