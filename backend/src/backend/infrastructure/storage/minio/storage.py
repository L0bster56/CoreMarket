import asyncio
from uuid import uuid4

import aioboto3

from src.backend.config import get_settings

_EXT_TO_MIME = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp", "avif": "image/avif"}

_session = aioboto3.Session()


class MinIOFileStorage:
    async def save(self, data: bytes, section: str, ext: str) -> str:
        settings = get_settings()
        filename = f"{uuid4()}.{ext}"
        key = f"{section}/{filename}"

        async with _session.client(
            "s3",
            endpoint_url=settings.MINIO_ENDPOINT,
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
        ) as client:
            await client.put_object(
                Bucket=settings.MINIO_BUCKET,
                Key=key,
                Body=data,
                ContentType=_EXT_TO_MIME.get(ext, "application/octet-stream"),
            )

        return key

    async def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        settings = get_settings()

        async with _session.client(
            "s3",
            endpoint_url=settings.MINIO_ENDPOINT,
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
        ) as client:
            url = await client.generate_presigned_url(
                "get_object",
                Params={"Bucket": settings.MINIO_BUCKET, "Key": key},
                ExpiresIn=expires_in,
            )

        return url.replace(settings.MINIO_ENDPOINT, settings.MINIO_PUBLIC_URL)

    async def get_presigned_urls(self, keys: list[str], expires_in: int = 3600) -> dict[str, str]:
        urls = await asyncio.gather(*[self.get_presigned_url(key, expires_in) for key in keys])
        return dict(zip(keys, urls))
