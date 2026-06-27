"""
Structured request logging middleware.

Emits one log line per HTTP request with:
  - request_id  (short random hex per request)
  - trace_id    (OTel W3C trace id; empty if OTel is not configured)
  - span_id     (OTel span id; empty if OTel is not configured)
  - method, path, status_code, duration_ms
"""

import logging
import time
import uuid
from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.backend.otel import get_trace_context

logger = logging.getLogger("coremarket.http")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = uuid.uuid4().hex[:8]
        start = time.monotonic()

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as exc:
            duration_ms = round((time.monotonic() - start) * 1000, 2)
            logger.error(
                "request_failed",
                exc_info=exc,
                extra={
                    "request_id": request_id,
                    **get_trace_context(),
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": 500,
                    "duration_ms": duration_ms,
                },
            )
            raise

        duration_ms = round((time.monotonic() - start) * 1000, 2)
        log_level = (
            logging.ERROR if status_code >= 500
            else logging.WARNING if status_code >= 400
            else logging.INFO
        )
        logger.log(
            log_level,
            "http_request",
            extra={
                "request_id": request_id,
                **get_trace_context(),
                "method": request.method,
                "path": request.url.path,
                "status_code": status_code,
                "duration_ms": duration_ms,
            },
        )
        return response
