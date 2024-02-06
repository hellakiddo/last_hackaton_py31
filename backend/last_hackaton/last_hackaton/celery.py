import os
from celery import Celery
from django.conf import settings

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE', 'last_hackaton.settings'
)

app = Celery(
    'last_hackaton', broker='redis://158.160.9.246:6379/0',backend='redis://158.160.9.246:6379/0',
)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_url = settings.CELERY_BROKER_URL
app.autodiscover_tasks()
