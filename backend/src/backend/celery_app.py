"""
Celery application configuration.

Queue layout:
  default     – lightweight ops (rating recalc, cleanup)
  emails      – welcome / transactional email delivery
  images      – thumbnail generation (CPU/IO heavy)
  search_sync – Elasticsearch index/delete
  homepage    – homepage snapshot precompute (scheduled)

Each queue has isolated concurrency so a large thumbnail backlog never
blocks email delivery.  Workers can be targeted per-queue with -Q flag.
"""

import logging
import time

from celery import Celery, Task
from celery.schedules import crontab
from celery.signals import task_failure, task_postrun, task_prerun, task_retry, worker_process_init

from src.backend.config import get_settings

settings = get_settings()

celery_app = Celery(
    "coremarket",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "src.backend.application.tasks.notifications",
        "src.backend.application.tasks.ratings",
        "src.backend.application.tasks.images",
        "src.backend.application.tasks.cleanup",
        "src.backend.application.tasks.search_sync",
        "src.backend.application.tasks.homepage",
    ],
)

celery_app.conf.update(
    # ── Serialisation ──────────────────────────────────────────────────────
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # ── Time ──────────────────────────────────────────────────────────────
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,

    # ── Worker tuning ─────────────────────────────────────────────────────
    worker_concurrency=settings.CELERY_WORKER_CONCURRENCY,
    task_always_eager=settings.CELERY_TASK_ALWAYS_EAGER,
    task_acks_late=True,
    worker_prefetch_multiplier=1,   # FIFO per queue; prevents starvation
    task_track_started=True,

    # ── Queue routing ─────────────────────────────────────────────────────
    task_default_queue="default",
    task_queues={
        "default":     {"exchange": "default",     "routing_key": "default"},
        "emails":      {"exchange": "emails",      "routing_key": "emails"},
        "images":      {"exchange": "images",      "routing_key": "images"},
        "search_sync": {"exchange": "search_sync", "routing_key": "search_sync"},
        "homepage":    {"exchange": "homepage",    "routing_key": "homepage"},
    },
    task_routes={
        "coremarket.tasks.send_welcome_email":       {"queue": "emails"},
        "coremarket.tasks.generate_thumbnail":       {"queue": "images"},
        "coremarket.tasks.index_item":               {"queue": "search_sync"},
        "coremarket.tasks.delete_item_from_index":   {"queue": "search_sync"},
        "coremarket.tasks.recalculate_item_rating":  {"queue": "default"},
        "coremarket.tasks.cleanup_expired_sessions": {"queue": "default"},
        "coremarket.tasks.compute_homepage_snapshot": {"queue": "homepage"},
    },

    # ── Beat schedule ──────────────────────────────────────────────────────
    beat_schedule={
        "cleanup-expired-sessions-daily": {
            "task": "coremarket.tasks.cleanup_expired_sessions",
            "schedule": crontab(hour=2, minute=0),
        },
        "homepage-snapshot-every-5m": {
            "task": "coremarket.tasks.compute_homepage_snapshot",
            "schedule": crontab(minute="*/5"),
        },
    },
)


# ── Worker init ────────────────────────────────────────────────────────────────

@worker_process_init.connect
def _setup_worker_logging(**kwargs: object) -> None:
    from src.backend.logging_setup import setup_logging
    setup_logging(level=settings.LOG_LEVEL, fmt=settings.LOG_FORMAT)
    logging.getLogger("celery").setLevel(logging.INFO)
    logging.getLogger("kombu").setLevel(logging.WARNING)


# ── Prometheus task metrics via Celery signals ─────────────────────────────────
# We track timing manually because the OTel instrumentation may not always be
# loaded inside worker processes.

_task_start_times: dict[str, float] = {}


def _queue_for(task: Task) -> str:
    """Best-effort queue name resolution from task routing config."""
    routes = celery_app.conf.task_routes or {}
    route = routes.get(task.name, {})
    return route.get("queue", "default")


@task_prerun.connect
def _on_task_prerun(task_id: str, task: Task, **kwargs: object) -> None:
    _task_start_times[task_id] = time.monotonic()
    try:
        from src.backend.metrics import celery_tasks_active
        celery_tasks_active.labels(queue=_queue_for(task)).inc()
    except Exception:
        pass


@task_postrun.connect
def _on_task_postrun(task_id: str, task: Task, retval: object, state: str, **kwargs: object) -> None:
    start = _task_start_times.pop(task_id, None)
    try:
        from src.backend.metrics import celery_task_duration_seconds, celery_tasks_active, celery_tasks_total
        queue = _queue_for(task)
        status = "success" if state == "SUCCESS" else "failure"
        celery_tasks_total.labels(task_name=task.name, queue=queue, status=status).inc()
        if start is not None:
            celery_task_duration_seconds.labels(task_name=task.name, queue=queue).observe(
                time.monotonic() - start
            )
        celery_tasks_active.labels(queue=queue).dec()
    except Exception:
        pass


@task_failure.connect
def _on_task_failure(
    task_id: str,
    sender: Task,
    exception: BaseException | None = None,
    **kwargs: object,
) -> None:
    _task_start_times.pop(task_id, None)
    try:
        from src.backend.metrics import celery_tasks_active, celery_tasks_total
        queue = _queue_for(sender)
        celery_tasks_total.labels(task_name=sender.name, queue=queue, status="failure").inc()
        celery_tasks_active.labels(queue=queue).dec()
    except Exception:
        pass

    try:
        from src.backend.infrastructure.notifications.telegram import send_telegram_alert
        exc_type = type(exception).__name__ if exception else "Unknown"
        exc_msg = str(exception)[:300] if exception else "—"
        retries = getattr(getattr(sender, "request", None), "retries", 0)
        msg = (
            f"🚨 <b>CoreMarket — Celery Task Failed</b>\n\n"
            f"<b>Task:</b> <code>{sender.name}</code>\n"
            f"<b>Error:</b> {exc_type}: {exc_msg}\n"
            f"<b>Retries:</b> {retries}\n"
            f"<b>Task ID:</b> <code>{task_id[:8]}</code>"
        )
        send_telegram_alert(msg)
    except Exception:
        pass


@task_retry.connect
def _on_task_retry(sender: Task, **kwargs: object) -> None:
    try:
        from src.backend.metrics import celery_tasks_total
        celery_tasks_total.labels(
            task_name=sender.name, queue=_queue_for(sender), status="retry"
        ).inc()
    except Exception:
        pass
