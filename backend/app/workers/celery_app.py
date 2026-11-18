from __future__ import annotations

from celery import Celery

from ..core.config import settings

celery_app = Celery(
    "clipforge",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.tasks"],
)
celery_app.conf.update(
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=86400,
)
