"""Celery application code."""
from celery import Celery
from flask import current_app
from app.shared.models.notebook import Notebook
import random
import time
import os

celery = Celery(__name__)  # We will update conf after app creation
celery.config_from_object("celery_settings")


@celery.task(bind=True)
def long_task(self):
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''
    total = random.randint(10, 50)
    for i in range(total):
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                              random.choice(adjective),
                                              random.choice(noun))
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': total,
                                'status': message})
        time.sleep(1)
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42}


@celery.task(bind=True)
def create_notebook(self, nbk_id=None):
    """Background process that creates an xlsx file from notebook data."""
    from app import create_app
    from boto.s3.connection import S3Connection
    this_app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    with this_app.app_context():
        conn = S3Connection(
            this_app.config['AWS_ACCESS_KEY_ID'],
            this_app.config['AWS_SECRET_ACCESS_KEY']
        )
        bucket = conn.get_bucket('pulsepodnotebooks')
        # Set the Amazon S3 filename:
        s3_filename = '%s.xlsx' % str(nbk_id)
        # filename = this_app.config['XLSX_PATH'] + '%s.xlsx' % str(nbk_id)
        # xlsx_file = '%s.xlsx' % str(nbk_id)
        # Create this key.
        key = bucket.new_key(s3_filename)
        bucket.set_acl('public-read', s3_filename)
        # Generate a URL for this key:
        url = key.generate_url(expires_in=0, query_auth=False)
        # Update the celery task with the URL:
        self.update_state(state='PROGESS', meta={'url': url})
        # Build the notebook:
        notebook = Notebook.objects(id=nbk_id).first()
        tmp_file = notebook.xls()
        key.set_contents_from_filename(tmp_file)
        return {'status': 'Task completed!', 'url': url}
