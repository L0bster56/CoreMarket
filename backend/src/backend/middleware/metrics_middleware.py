"""
Prometheus HTTP metrics middleware.

Tracks per-endpoint request count, latency histogram, and in-progress gauge.
Endpoints are normalised (path params replaced by placeholders) so cardinality
stays bounded even with UUID-heavy routes like /items/{id}.
"""

import re
import time
from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.backend.metrics import (
    http_request_duration_seconds,
    http_requests_in_progress,
    http_requests_total,
)

# Patterns ordered most-specific → least-specific
_PATH_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"/items/[^/]+/gallery/[^/]+"), "/items/{id}/gallery/{image_id}"),
    (re.compile(r"/items/[^/]+/characteristics/[^/]+"), "/items/{id}/characteristics/{char_id}"),
    (re.compile(r"/items/[^/]+/tags/[^/]+"), "/items/{id}/tags/{tag_id}"),
    (re.compile(r"/items/[^/]+/gallery"), "/items/{id}/gallery"),
    (re.compile(r"/items/[^/]+/characteristics"), "/items/{id}/characteristics"),
    (re.compile(r"/items/[^/]+/tags"), "/items/{id}/tags"),
    (re.compile(r"/items/[^/]+"), "/items/{id}"),
    (re.compile(r"/categories/[^/]+"), "/categories/{id}"),
    (re.compile(r"/tags/[^/]+"), "/tags/{id}"),
    (re.compile(r"/users/[^/]+"), "/users/{id}"),
    (re.compile(r"/comments/[^/]+"), "/comments/{id}"),
    (re.compile(r"/ratings/[^/]+"), "/ratings/{id}"),
    (re.compile(r"/blog/[^/]+"), "/blog/{slug}"),
]

# Skip metrics collection for these paths (noisy, low value)
_SKIP_PATHS = frozenset({"/metrics", "/health", "/api/v1/health"})


def _normalise_path(path: str) -> str:
    for pattern, replacement in _PATH_PATTERNS:
        if pattern.search(path):
            return pattern.sub(replacement, path)
    return path


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        if path in _SKIP_PATHS:
            return await call_next(request)

        method = request.method
        endpoint = _normalise_path(path)

        http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()
        start = time.perf_counter()

        try:
            response = await call_next(request)
            status_code = str(response.status_code)
        except Exception:
            status_code = "500"
            raise
        finally:
            duration = time.perf_counter() - start
            http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()
            http_request_duration_seconds.labels(
                method=method, endpoint=endpoint
            ).observe(duration)
            http_requests_total.labels(
                method=method, endpoint=endpoint, status_code=status_code
            ).inc()

        return response
