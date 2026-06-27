import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from jose import JWTError
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from src.backend.application.shared.errors import (
    BadRequestError,
    ConflictError,
    NotAuthorizedError,
    NotFoundError,
)
from src.backend.config import get_settings
from src.backend.logging_setup import setup_logging
from src.backend.middleware.logging_middleware import RequestLoggingMiddleware
from src.backend.middleware.metrics_middleware import MetricsMiddleware
from src.backend.presentation.api.v1.blog.router import router as blog_router
from src.backend.presentation.api.v1.storage.router import router as storage_router
from src.backend.presentation.api.v1.auth.router import auth_rate_router, router as auth_router
from src.backend.presentation.api.v1.category.router import router as category_router
from src.backend.presentation.api.v1.comment.router import router as comment_router
from src.backend.presentation.api.v1.core.handlers import (
    bad_request_exception_handler,
    conflict_exception_handler,
    jwt_exception_handler,
    not_authorized_exception_handler,
    not_found_exception_handler,
)
from src.backend.presentation.api.v1.core.limiter import limiter
from src.backend.presentation.api.v1.homepage.router import router as homepage_router
from src.backend.presentation.api.v1.item.router import router as item_router
from src.backend.presentation.api.v1.rating.router import router as rating_router
from src.backend.presentation.api.v1.search.router import router as search_router
from src.backend.presentation.api.v1.tag.router import router as tag_router
from src.backend.presentation.api.v1.upload.router import router as upload_router
from src.backend.presentation.api.v1.user.router import router as user_router

settings = get_settings()
setup_logging(level=settings.LOG_LEVEL, fmt=settings.LOG_FORMAT)

logger = logging.getLogger("coremarket.app")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # ── OpenTelemetry ────────────────────────────────────────────────────────
    from src.backend.otel import setup_otel
    setup_otel(app)

    # ── Elasticsearch index ──────────────────────────────────────────────────
    if settings.SEARCH_ENABLED:
        try:
            from src.backend.search.infrastructure.elasticsearch.client import get_es_client
            from src.backend.search.infrastructure.elasticsearch.indexes.items import ItemIndex

            es = get_es_client()
            item_index = ItemIndex(es, settings.ELASTICSEARCH_INDEX_PREFIX)
            await item_index.ensure_index()
            logger.info(
                "search_ready",
                extra={"index": item_index.index_name, "url": settings.ELASTICSEARCH_URL},
            )
        except Exception as exc:
            logger.warning(
                "search_startup_failed",
                exc_info=exc,
                extra={"url": settings.ELASTICSEARCH_URL},
            )

    yield

    if settings.SEARCH_ENABLED:
        try:
            from src.backend.search.infrastructure.elasticsearch.client import close_es_client
            await close_es_client()
        except Exception:
            pass


app = FastAPI(title="CoreMarket API", version="1.0.0", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(NotFoundError, not_found_exception_handler)
app.add_exception_handler(ConflictError, conflict_exception_handler)
app.add_exception_handler(BadRequestError, bad_request_exception_handler)
app.add_exception_handler(NotAuthorizedError, not_authorized_exception_handler)
app.add_exception_handler(JWTError, jwt_exception_handler)


async def _unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        "unhandled_exception",
        exc_info=exc,
        extra={"method": request.method, "path": request.url.path},
    )
    try:
        import asyncio
        from src.backend.infrastructure.notifications.telegram import async_send_telegram_alert
        exc_str = f"{type(exc).__name__}: {exc}"[:300]
        msg = (
            f"🚨 <b>CoreMarket Alert</b>\n\n"
            f"<b>Service:</b> backend\n"
            f"<b>Level:</b> ERROR\n"
            f"<b>Endpoint:</b> {request.method} {request.url.path}\n"
            f"<b>Error:</b> {exc_str}"
        )
        asyncio.create_task(async_send_telegram_alert(msg))
    except Exception:
        pass
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "status_code": 500},
    )


app.add_exception_handler(Exception, _unhandled_exception_handler)

# Metrics middleware must wrap after exception handlers so exceptions are counted
app.add_middleware(MetricsMiddleware)
app.add_middleware(RequestLoggingMiddleware)


# ── Built-in endpoints ────────────────────────────────────────────────────────

@app.get("/health", include_in_schema=False)
@app.get("/api/v1/health", include_in_schema=False)
async def health_check() -> JSONResponse:
    return JSONResponse({"status": "ok", "version": "1.0.0"})


@app.get("/metrics", include_in_schema=False)
async def prometheus_metrics() -> Response:
    """Prometheus scrape endpoint — collected by prom/prometheus."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


# ── API routers ───────────────────────────────────────────────────────────────

_PREFIX = "/api/v1"

app.include_router(auth_rate_router, prefix=_PREFIX)
app.include_router(auth_router, prefix=_PREFIX)
app.include_router(user_router, prefix=_PREFIX)
app.include_router(category_router, prefix=_PREFIX)
app.include_router(tag_router, prefix=_PREFIX)
app.include_router(item_router, prefix=_PREFIX)
app.include_router(comment_router, prefix=_PREFIX)
app.include_router(rating_router, prefix=_PREFIX)
app.include_router(upload_router, prefix=_PREFIX)
app.include_router(blog_router, prefix=_PREFIX)
app.include_router(storage_router, prefix=_PREFIX)
app.include_router(search_router, prefix=_PREFIX)
app.include_router(homepage_router, prefix=_PREFIX)
