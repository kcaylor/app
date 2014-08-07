from .. import db
import datetime
from flask import current_app


class Pod(db.Document):

    MODES = ['inactive', 'teenager', 'asleep', 'normal']
    RADIOS = ['gsm', 'cdma', 'wcdma', 'wifi', 'irridium']

    name = db.StringField()
    owner = db.ReferenceField('User')
    pod_id = db.IntField()
    qr = db.StringField(
        default='https://s3.amazonaws.com/pulsepodqrsvgs/default.svg'
    )
    imei = db.StringField(
        default='000000000000000'
    )
    radio = db.StringField(
        choices=RADIOS,
        default='gsm'
    )
    mode = db.StringField(
        choices=MODES,
        default='asleep'
    )
    number = db.StringField(
        default='18005551212'
    )
    last = db.DateTimeField(
        default=datetime.datetime.now())
    current_notebook = db.ReferenceField('Notebook')
    notebooks = db.IntField(
        default=0
    )
    observations = db.IntField(
        default=0
    )
    about = db.StringField(
        default=''
    )

    meta = {
        'collection': 'pods',
        'indexes': [
            'name', 'pod_id', 'number', 'mode', 'owner'],
        'index_background': True,
        'ordering': ['-last'],
    }

    def __repr__(self):
        return '<Pod %r>' % self.name

    def get_id(self):
        return unicode(self.id)

    @staticmethod
    def generate_fake(count=100):
        from random import choice, randint, sample
        from faker import Faker
        from .user import User
        import phonenumbers
        nusers = User.objects().count()
        fake = Faker()
        # fake.seed(3123)
        fake_pods = []
        for i in range(count):
            if nusers > 0:
                user = User.objects()[randint(0, nusers-1)]
            else:
                user = User.generate_fake(1)[0]
            pod = Pod(
                name=fake.first_name() + '-' + fake.last_name() + '-' +
                str(fake.random_int(min=1000)),
                owner=user,
                pod_id=fake.random_int(min=20),
                qr='https://s3.amazonaws.com/pulsepodqrsvgs/default.svg',
                imei=str(randint(100000000000000, 999999999999999)),
                radio='gsm',
                mode=choice(['normal', 'teenager', 'asleep', 'inactive']),
                number=phonenumbers.format_number(
                    phonenumbers.parse(fake.phone_number(), 'US'),
                    phonenumbers.PhoneNumberFormat.E164),
            )
            try:
                pod.save()
                fake_pods.append(pod)
            except:
                "Pod save failed"
        return fake_pods

    def create_qr(self):
        # Set up the file names
        tmp_file = 'tmp.svg'
        pod_qr_file = '%s.svg' % self.name
        try:
            # Now we can generate the bitly url:
            c = bitly_api.Connection(
                access_token=current_app.config['BITLY_API_TOKEN']
            )
            bitly_link = c.shorten(url)['url']

            # Update the link title to this pod name:
            c.user_link_edit(bitly_link, 'title', str(self.name))
            # Add this link to the PulsePod bundle:
            a = c.bundle_bundles_by_user()['bundles']
            bundle_link = a[next(index for (index, d) in enumerate(a)
                                 if d["title"] == "PulsePods")]['bundle_link']
            c.bundle_link_add(bundle_link, bitly_link)
        except:
            return "Error creating Bitly link"

        try:
            # Make the QR Code:
            img = qrcode.make(
                bitly_link,
                image_factory=qrcode.image.svg.SvgPathImage)
            f = open(tmp_file, 'w')
            img.save(f)
            f.close()
        except:
            return "Error in making QR code file"

        try:
            # UPLOAD THE QRFILE TO S3:
            conn = S3Connection(current_app.config['AWS_ACCESS_KEY_ID'],
                                current_app.config['AWS_SECRET_ACCESS_KEY'])
            bucket = conn.get_bucket('pulsepodqrsvgs')
            k = Key(bucket)
            k.key = pod_qr_file
            k.set_contents_from_filename(tmp_file)
            bucket.set_acl('public-read', pod_qr_file)
        except:
            return "Error writing file to Amazon S3"

        return "QR file successfully created"
