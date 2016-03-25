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
    this_app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    with this_app.app_context():
        notebook = Notebook.objects(id=nbk_id).first()
        filename = current_app.config['XLSX_PATH'] + '%s.xlsx' % str(nbk_id)
        self.update_state(state='PROGESS')
        notebook.xls(filename=filename)
        return {'status': 'Task completed!', 'filename': filename}
