import os
from redis import Redis
import urlparse

from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

urlparse.uses_netloc.append('redis')
url = urlparse.urlparse(str(os.getenv('REDISTOGO_URL')).replace("'", ""))
conn = Redis(host=url.hostname, port=url.port, db=0, password=url.password)

if __name__ == '__main__':
    from app import create_app
    with Connection(conn):
        this_app = create_app(os.getenv('FLASK_CONFIG') or 'default')
        with this_app.app_context():
            worker = Worker(map(Queue, listen))
            worker.work()
