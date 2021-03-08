import os

from celery.schedules import crontab
from django.conf import settings
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'covid_stats.settings')

app = Celery('myceleryapp')

CELERY_TIMEZONE = 'UTC'

app.config_from_object('django.conf:settings')    

app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'
app.conf.beat_schedule = {
    "test-task-job": {
        "task": "account.tasks.test_task_job",
        "schedule": crontab(minute='*/1'),
        "args": ()
    },
}
app.conf.accept_content = settings.CELERY_ACCEPT_CONTENT
app.conf.task_serializer = settings.CELERY_TASK_SERIALIZER
app.conf.result_serializer = settings.CELERY_RESULT_SERIALIZER
app.conf.worker_prefetch_multiplier = \
    settings.CELERY_WORKER_PREFETCH_MULTIPLIER
# To restart worker processes after every task
app.conf.broker_url = settings.BROKER_URL
app.conf.broker_transport_options = settings.BROKER_TRANSPORT_OPTIONS
app.conf.result_backend = settings.CELERY_RESULT_BACKEND

app.autodiscover_tasks()