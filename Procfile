release: python manage.py migrate --settings=config.settings.production
web: gunicorn config.wsgi --log-file -
