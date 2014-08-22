#!/usr/bin/env python
import os
COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()
    print('Starting coverage')

if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

from app import create_app, db
from app.models.user import User
from app.models.pod import Pod
from app.models.data import Data
from app.models.sensor import Sensor
from app.models.notebook import Notebook
from app.models.message import Message
from flask.ext.script import Manager, Shell


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    return dict(
        app=app,
        db=db,
        User=User,
        Pod=Pod,
        Data=Data,
        Sensor=Sensor,
        Notebook=Notebook,
    )

manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
def test(coverage=False):
    """Run the unit tests (using nose)"""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        print('Restarting script...')
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import nose
    if COV:
        print('Ending coverage')
        COV.stop()
        COV.save()
        print('Coverage Summary')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print ('HTML Version: file://%s/index.html' % covdir)
        COV.erase()
    nose.main(argv=[''])


@manager.command
def reset():
    """Reset the testing database"""
    if app.testing:
        print "Reseting testing database"
        print "\t...dropping old collections"
        User.drop_collection()
        Pod.drop_collection()
        Notebook.drop_collection()
        Data.drop_collection()
        Sensor.drop_collection()
        Message.drop_collection()
        print "\t...generating new fake data"
        Sensor.generate_fake(15)
        User.generate_fake(10)
        Pod.generate_fake(20)
        Notebook.generate_fake(40)
        Data.generate_fake(300)
        Message.generate_fake(100)
        for notebook in Notebook.objects():
            notebook.observations = Data.objects(notebook=notebook).count()
            notebook.save()
    else:
        print "Cannot run this command under %s config" % \
            app.config['FLASK_CONFIG']


@manager.command
def serve():
    """Starts the app (using waitress)"""
    from waitress import serve
    port = int(os.getenv('PORT', 5000))
    serve(app, port=port)

if __name__ == '__main__':
    manager.run()
