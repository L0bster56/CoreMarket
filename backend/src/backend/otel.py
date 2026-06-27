"""
OpenTelemetry SDK bootstrap for CoreMarket.

Call `setup_otel(app)` once from the FastAPI lifespan *before* any routes
are exercised.  If OTEL_ENABLED=false the function is a no-op, so the
rest of the code (trace_id in logs, etc.) degrades gracefully to empty
strings via the SDK's NoOp tracer.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import FastAPI

logger = logging.getLogger("coremarket.otel")


def setup_otel(app: "FastAPI") -> None:
    from src.backend.config import get_settings

    settings = get_settings()
    if not settings.OTEL_ENABLED:
        logger.info("otel_disabled", extra={"reason": "OTEL_ENABLED=false"})
        return

    try:
        _configure_tracer(settings)
        _instrument_libraries(app)
        logger.info(
            "otel_configured",
            extra={
                "endpoint": settings.OTEL_ENDPOINT,
                "service": settings.OTEL_SERVICE_NAME,
            },
        )
    except Exception as exc:
        # OTel must never crash the app — degrade gracefully
        logger.warning("otel_setup_failed", exc_info=exc)


def _configure_tracer(settings: object) -> None:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.resources import SERVICE_NAME
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    resource = Resource(attributes={SERVICE_NAME: settings.OTEL_SERVICE_NAME})
    provider = TracerProvider(resource=resource)

    exporter = OTLPSpanExporter(
        endpoint=settings.OTEL_ENDPOINT,
        insecure=True,
    )
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)


def _instrument_libraries(app: "FastAPI") -> None:
    from opentelemetry.instrumentation.celery import CeleryInstrumentor
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.redis import RedisInstrumentor
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

    FastAPIInstrumentor.instrument_app(app)
    SQLAlchemyInstrumentor().instrument()
    RedisInstrumentor().instrument()
    CeleryInstrumentor().instrument()


def get_trace_context() -> dict[str, str]:
    """Return trace_id / span_id for the current OTel span (empty if none)."""
    try:
        from opentelemetry import trace

        span = trace.get_current_span()
        ctx = span.get_span_context()
        if ctx and ctx.is_valid:
            return {
                "trace_id": format(ctx.trace_id, "032x"),
                "span_id": format(ctx.span_id, "016x"),
            }
    except Exception:
        pass
    return {"trace_id": "", "span_id": ""}
