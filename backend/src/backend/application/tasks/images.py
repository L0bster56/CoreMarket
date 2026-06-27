import asyncio
import io
import logging
import time
from pathlib import PurePosixPath

from celery import Task

from src.backend.celery_app import celery_app

logger = logging.getLogger("coremarket.tasks.images")

_THUMB_QUALITY = 85


async def _generate_thumbnail_async(key: str, width: int, height: int) -> str:
    import aioboto3
    from PIL import Image

    from src.backend.config import get_settings

    settings = get_settings()
    session = aioboto3.Session()

    s3_kwargs = dict(
        endpoint_url=settings.MINIO_ENDPOINT,
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY,
    )

    # Download original image
    async with session.client("s3", **s3_kwargs) as client:
        response = await client.get_object(Bucket=settings.MINIO_BUCKET, Key=key)
        data: bytes = await response["Body"].read()

    # Generate thumbnail with Pillow
    img = Image.open(io.BytesIO(data))
    img = img.convert("RGB")
    img.thumbnail((width, height), Image.LANCZOS)
    output = io.BytesIO()
    img.save(output, format="JPEG", quality=_THUMB_QUALITY, optimize=True)
    thumb_data = output.getvalue()

    # Build thumbnail key: <section>/thumb_<uuid>.jpg
    path = PurePosixPath(key)
    thumb_key = str(path.parent / f"thumb_{path.stem}.jpg")

    # Upload thumbnail
    async with session.client("s3", **s3_kwargs) as client:
        await client.put_object(
            Bucket=settings.MINIO_BUCKET,
            Key=thumb_key,
            Body=thumb_data,
            ContentType="image/jpeg",
        )

    return thumb_key


@celery_app.task(
    name="coremarket.tasks.generate_thumbnail",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    acks_late=True,
)
def generate_thumbnail(self: Task, key: str, width: int = 400, height: int = 300) -> dict:
    start = time.monotonic()
    task_id = self.request.id

    logger.info(
        "task_started",
        extra={
            "task_id": task_id,
            "task_name": self.name,
            "key": key,
            "width": width,
            "height": height,
        },
    )

    try:
        thumb_key = asyncio.run(_generate_thumbnail_async(key, width, height))
        duration_ms = int((time.monotonic() - start) * 1000)
        logger.info(
            "task_completed",
            extra={
                "task_id": task_id,
                "task_name": self.name,
                "key": key,
                "thumb_key": thumb_key,
                "status": "success",
                "duration_ms": duration_ms,
            },
        )
        return {"thumb_key": thumb_key}

    except Exception as exc:
        duration_ms = int((time.monotonic() - start) * 1000)
        logger.error(
            "task_failed",
            exc_info=exc,
            extra={
                "task_id": task_id,
                "task_name": self.name,
                "key": key,
                "duration_ms": duration_ms,
                "retry": self.request.retries,
            },
        )
        raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))
