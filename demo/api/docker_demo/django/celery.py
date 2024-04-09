import os

from celery import Celery

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "docker_demo.django.settings"
)

app = Celery("docker-demo")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
