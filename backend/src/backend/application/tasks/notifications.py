import asyncio
import logging
import time
from uuid import UUID

from celery import Task

from src.backend.celery_app import celery_app

logger = logging.getLogger("coremarket.tasks.notifications")


async def _fetch_user_email(user_id: str) -> str | None:
    """Query DB for user email. Returns None if user not found."""
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

    from src.backend.config import get_settings

    settings = get_settings()
    engine = create_async_engine(settings.ASYNC_DATABASE_URL, pool_pre_ping=True)
    try:
        async with AsyncSession(engine) as session:
            result = await session.execute(
                text("SELECT email, username FROM users WHERE id = :uid"),
                {"uid": user_id},
            )
            row = result.fetchone()
            return (row.email, row.username) if row else None
    finally:
        await engine.dispose()


def _send_email(to_email: str, username: str) -> None:
    """
    Placeholder for real SMTP delivery.
    Replace this body with smtplib/aiosmtplib when SMTP settings are configured.
    """
    from src.backend.config import get_settings

    settings = get_settings()
    smtp_host = getattr(settings, "SMTP_HOST", None)
    if smtp_host:
        import smtplib
        from email.mime.text import MIMEText

        msg = MIMEText(
            f"Hi {username}, welcome to CoreMarket! Your account is ready.",
            "plain",
            "utf-8",
        )
        msg["Subject"] = "Welcome to CoreMarket"
        msg["From"] = getattr(settings, "SMTP_FROM", "noreply@coremarket.local")
        msg["To"] = to_email
        with smtplib.SMTP(smtp_host, getattr(settings, "SMTP_PORT", 587)) as smtp:
            smtp.sendmail(msg["From"], [to_email], msg.as_string())
    else:
        logger.info("smtp_not_configured_skipping_delivery", extra={"to": to_email})


@celery_app.task(
    name="coremarket.tasks.send_welcome_email",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
)
def send_welcome_email(self: Task, user_id: str) -> dict:
    start = time.monotonic()
    task_id = self.request.id

    logger.info(
        "task_started",
        extra={"task_id": task_id, "task_name": self.name, "user_id": user_id},
    )

    try:
        row = asyncio.run(_fetch_user_email(user_id))
        if row is None:
            logger.warning(
                "user_not_found_skipping_email",
                extra={"task_id": task_id, "user_id": user_id},
            )
            return {"status": "skipped", "reason": "user_not_found"}

        email, username = row
        _send_email(email, username)

        duration_ms = int((time.monotonic() - start) * 1000)
        logger.info(
            "task_completed",
            extra={
                "task_id": task_id,
                "task_name": self.name,
                "user_id": user_id,
                "status": "success",
                "duration_ms": duration_ms,
            },
        )
        return {"status": "sent", "to": email}

    except Exception as exc:
        duration_ms = int((time.monotonic() - start) * 1000)
        logger.error(
            "task_failed",
            exc_info=exc,
            extra={
                "task_id": task_id,
                "task_name": self.name,
                "user_id": user_id,
                "duration_ms": duration_ms,
                "retry": self.request.retries,
            },
        )
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
