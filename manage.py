#!/usr/bin/python
import os
from app import create_app, db
from app.models import User, Pod, Data
from flask.ext.script import Manager, Shell
from flask.ext.assets import ManageAssets

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    return dict(
        app=app,
        db=db,
        User=User,
        Pod=Pod,
        Data=Data
    )
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("assets", ManageAssets())
manager.add_option('-c', '--config', dest='config', required=False)


@manager.command
def test():
    """Run the tests (using nose)"""
    import nose
    nose.main(argv=[''])

if __name__ == '__main__':
    manager.run()
