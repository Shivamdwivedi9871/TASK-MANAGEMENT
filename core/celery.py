import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "test-daily-favorite-summary": {
        "task": "favorites.tasks.send_daily_favorite",
        "schedule": 60.0,
    },
}
