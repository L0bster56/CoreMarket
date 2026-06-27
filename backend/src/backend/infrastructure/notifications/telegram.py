"""
Telegram alert sender.

Sends plain text messages via Telegram Bot API using httpx (sync).
Redis cooldown prevents duplicate alerts (same fingerprint → 5-minute silence).
Never raises to the caller — all errors are caught and logged.

Usage (sync, from Celery workers):
    from src.backend.infrastructure.notifications.telegram import send_telegram_alert
    send_telegram_alert("🚨 Something broke")

Usage (async, from FastAPI handlers):
    from src.backend.infrastructure.notifications.telegram import async_send_telegram_alert
    asyncio.create_task(async_send_telegram_alert("🚨 Something broke"))
"""

import asyncio
import hashlib
import logging
import time
from typing import Optional

import httpx
import redis as redis_lib

logger = logging.getLogger("coremarket.notifications.telegram")

_COOLDOWN_TTL = 300        # seconds — same alert fingerprint is silent for 5 min
_HTTP_TIMEOUT = 5.0        # seconds per attempt
_RETRY_COUNT = 2           # total extra attempts after the first
_RETRY_DELAY = 1.0         # seconds between retries
_REDIS_COOLDOWN_DB = 2     # separate Redis db to isolate cooldown keys
_TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"
_MAX_MSG_LEN = 4096        # Telegram hard limit


def _get_redis() -> Optional[redis_lib.Redis]:
    """Return a Redis client for cooldown tracking, or None if unavailable."""
    try:
        from src.backend.config import get_settings
        url = get_settings().REDIS_URL
        # Switch to db 2 for alert cooldown keys
        base = url.rsplit("/", 1)[0] if "/" in url.split("//", 1)[-1] else url
        cooldown_url = f"{base}/{_REDIS_COOLDOWN_DB}"
        client: redis_lib.Redis = redis_lib.Redis.from_url(cooldown_url, decode_responses=True, socket_connect_timeout=2)
        client.ping()
        return client
    except Exception as exc:
        logger.debug("telegram_cooldown_redis_unavailable: %s", exc)
        return None


def _fingerprint(message: str) -> str:
    """Hash the first 200 chars of the message for dedup keying."""
    first = message.split("\n")[0][:200]
    return hashlib.sha256(first.encode()).hexdigest()[:16]


def _is_cooled_down(client: Optional[redis_lib.Redis], fp: str) -> bool:
    if client is None:
        return False
    try:
        return bool(client.exists(f"tg:cd:{fp}"))
    except Exception:
        return False


def _mark_sent(client: Optional[redis_lib.Redis], fp: str) -> None:
    if client is None:
        return
    try:
        client.setex(f"tg:cd:{fp}", _COOLDOWN_TTL, "1")
    except Exception:
        pass


def send_telegram_alert(message: str) -> None:
    """
    Send a Telegram message. Safe to call from any synchronous context.
    Silently absorbs all errors — never affects the caller's control flow.
    """
    try:
        from src.backend.config import get_settings
        settings = get_settings()

        if not getattr(settings, "TELEGRAM_ALERTS_ENABLED", False):
            return

        token: str = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
        chat_id: str = str(getattr(settings, "TELEGRAM_CHAT_ID", ""))
        if not token or not chat_id:
            return

        text = message[:_MAX_MSG_LEN]
        fp = _fingerprint(text)
        redis_client = _get_redis()

        if _is_cooled_down(redis_client, fp):
            logger.debug("telegram_suppressed fingerprint=%s", fp)
            return

        url = _TELEGRAM_API.format(token=token)
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}

        for attempt in range(1, _RETRY_COUNT + 2):
            try:
                resp = httpx.post(url, json=payload, timeout=_HTTP_TIMEOUT)
                if resp.status_code == 200:
                    _mark_sent(redis_client, fp)
                    logger.info("telegram_sent fingerprint=%s", fp)
                    return
                # 429 = rate limited; 400 = bad request (likely config error)
                logger.warning(
                    "telegram_http_error status=%d attempt=%d body=%.120s",
                    resp.status_code, attempt, resp.text,
                )
                if resp.status_code in (400, 401, 403):
                    break  # Config error — no point retrying
            except httpx.TimeoutException:
                logger.warning("telegram_timeout attempt=%d", attempt)
            except Exception as exc:
                logger.warning("telegram_request_error attempt=%d: %s", attempt, exc)
                break

            if attempt <= _RETRY_COUNT:
                time.sleep(_RETRY_DELAY)

    except Exception as exc:
        try:
            logger.error("telegram_fatal: %s", exc)
        except Exception:
            pass


async def async_send_telegram_alert(message: str) -> None:
    """Async wrapper — runs send_telegram_alert in the default thread pool."""
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, send_telegram_alert, message)
