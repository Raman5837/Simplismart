from __future__ import absolute_import, unicode_literals

from os import environ

from celery import Celery

environ.setdefault("DJANGO_SETTINGS_MODULE", "hypervisor.settings")

app = Celery("hypervisor")

# Load task modules from all registered Django app configs.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Autodiscover tasks from installed apps
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
