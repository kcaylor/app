"""Celery application code."""
from celery import Celery
from app import create_app
import os
import time
import requests

celery = Celery(__name__)
celery.config_from_object("celery_settings")
celery.control.purge()  # Purge the job queue on startup.


def upload_status(amount, total):
    """Callback function for boto S3 upload."""
    pass


@celery.task(bind=True)
def create_xls_notebook(self, nbk_id=None):
    """Background process that creates an xlsx file from notebook data."""
    from boto.s3.connection import S3Connection
    this_app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    # Guess the URL and update the link before anything else.
    url = 'https://pulsepodnotebooks.s3.amazonaws.com/{id}.xlsx'.format(
        id=nbk_id)
    # self.update_state(state='PROGESS', meta={'url': url, 'nbk_id': nbk_id})
    with this_app.app_context():
        conn = S3Connection(
            this_app.config['AWS_ACCESS_KEY_ID'],
            this_app.config['AWS_SECRET_ACCESS_KEY']
        )
        bucket = conn.get_bucket('pulsepodnotebooks')
        # Set the Amazon S3 filename:
        s3_filename = '%s.xlsx' % str(nbk_id)
        # Create this key.
        key = bucket.new_key(s3_filename)
        # key.set_contents_from_string('temp')  # need something to make URL.
        # Build the notebook:
        from app.shared.models.notebook import Notebook
        notebook = Notebook.objects(id=nbk_id).first()
        tmp_file = notebook.xls()
        tmp_size = float(os.path.getsize(tmp_file))
        key.set_contents_from_filename(tmp_file, cb=upload_status)
        url = key.generate_url(expires_in=0, query_auth=False)
        bucket.set_acl('public-read', s3_filename)
        self.update_state(
            state='PROGESS',
            meta={
                'url': url,
                'nbk_id': nbk_id,
                's3_size': 1,
                'tmp_size': tmp_size
            }
        )
        for i in range(10):
            resp = requests.head(url)
            size = float(resp.headers['content-length'])
            self.update_state(
                state='PROGESS',
                meta={
                    'url': url,
                    'nbk_id': nbk_id,
                    's3_size': size,
                    'tmp_size': tmp_size
                }
            )
            if size >= tmp_size * .95:
                break
            else:
                time.sleep(1)  # wait one second for upload to continue.
        return {'status': 'Task completed!', 'url': url}
