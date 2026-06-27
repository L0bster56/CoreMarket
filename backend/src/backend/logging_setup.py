import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any


class JSONFormatter(logging.Formatter):
    """Serializes log records as single-line JSON for Loki ingestion."""

    def format(self, record: logging.LogRecord) -> str:
        entry: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }

        # Request fields injected via extra={}
        for field in ("request_id", "method", "path", "status_code", "duration_ms"):
            if (val := getattr(record, field, None)) is not None:
                entry[field] = val

        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(entry, ensure_ascii=False)


class ConsoleFormatter(logging.Formatter):
    _FMT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
    _DATE = "%Y-%m-%dT%H:%M:%S"

    def __init__(self) -> None:
        super().__init__(fmt=self._FMT, datefmt=self._DATE)


def setup_logging(level: str = "INFO", fmt: str = "json") -> None:
    """Configure root logger once at application startup."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    formatter: logging.Formatter = JSONFormatter() if fmt == "json" else ConsoleFormatter()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(log_level)

    # Take over uvicorn's own loggers so their output goes through JSON formatter.
    # uvicorn calls logging.config.dictConfig() before importing the app module,
    # which attaches its own handlers to "uvicorn" and "uvicorn.error".
    # We clear those handlers and let them propagate to root (JSON handler).
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        lgr = logging.getLogger(name)
        lgr.handlers.clear()
        lgr.propagate = True

    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("aiobotocore").setLevel(logging.WARNING)
