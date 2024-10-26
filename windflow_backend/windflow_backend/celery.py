import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'windflow_backend.settings')

app = Celery('windflow_backend')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
