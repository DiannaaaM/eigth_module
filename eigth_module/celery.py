import os

from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eigth_module.settings")

app = Celery("eigth_module")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

