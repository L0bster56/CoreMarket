"""
Centralised Prometheus metric definitions for CoreMarket.

All metrics use the `coremarket_` prefix so they never clash with
exporters (node, cadvisor, postgres, redis, es) that run in parallel.

Import only the symbols you need – this module is imported once and
the Prometheus default registry retains all defined collectors.
"""

from prometheus_client import REGISTRY, Counter, Gauge, Histogram

# ── latency buckets suited for a web API (ms range up to 10 s) ────────────
_HTTP_BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
_TASK_BUCKETS = (0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0)

# ── HTTP / FastAPI ─────────────────────────────────────────────────────────

http_requests_total = Counter(
    "coremarket_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

http_request_duration_seconds = Histogram(
    "coremarket_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=_HTTP_BUCKETS,
)

http_requests_in_progress = Gauge(
    "coremarket_http_requests_in_progress",
    "HTTP requests currently being processed",
    ["method", "endpoint"],
)

# ── Celery tasks ───────────────────────────────────────────────────────────

celery_tasks_total = Counter(
    "coremarket_celery_tasks_total",
    "Total Celery task executions",
    ["task_name", "queue", "status"],   # status: success | failure | retry
)

celery_task_duration_seconds = Histogram(
    "coremarket_celery_task_duration_seconds",
    "Celery task execution time in seconds",
    ["task_name", "queue"],
    buckets=_TASK_BUCKETS,
)

celery_tasks_active = Gauge(
    "coremarket_celery_tasks_active",
    "Number of Celery tasks currently executing",
    ["queue"],
)

# ── Homepage snapshot ──────────────────────────────────────────────────────

homepage_requests_total = Counter(
    "coremarket_homepage_requests_total",
    "Homepage endpoint requests by cache source",
    ["source"],  # source: cache_hit | cache_miss | fallback
)

homepage_snapshot_age_seconds = Gauge(
    "coremarket_homepage_snapshot_age_seconds",
    "Seconds since last homepage snapshot was computed (0 = fresh)",
)

# ── Search ─────────────────────────────────────────────────────────────────

search_requests_total = Counter(
    "coremarket_search_requests_total",
    "Total search endpoint requests",
    ["kind"],   # kind: items | suggestions
)

search_duration_seconds = Histogram(
    "coremarket_search_duration_seconds",
    "Elasticsearch query latency in seconds",
    ["kind"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5),
)

__all__ = [
    "REGISTRY",
    "http_requests_total",
    "http_request_duration_seconds",
    "http_requests_in_progress",
    "celery_tasks_total",
    "celery_task_duration_seconds",
    "celery_tasks_active",
    "homepage_requests_total",
    "homepage_snapshot_age_seconds",
    "search_requests_total",
    "search_duration_seconds",
]
