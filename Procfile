# Procfile for app
web: NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program python -u manage.py serve
worker: celery worker -A tasks.celery -l INFO


