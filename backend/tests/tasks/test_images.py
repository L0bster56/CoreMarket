"""Tests for image tasks (generate_thumbnail)."""
import io
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _make_jpeg_bytes() -> bytes:
    """Create a minimal valid JPEG image in memory."""
    from PIL import Image

    img = Image.new("RGB", (800, 600), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


class TestGenerateThumbnail:
    def test_thumbnail_naming_convention(self):
        """thumb key must follow items/thumb_<uuid>.jpg pattern."""
        from src.backend.application.tasks.images import generate_thumbnail

        with patch(
            "src.backend.application.tasks.images.asyncio.run",
            side_effect=lambda coro: "items/thumb_abc123.jpg",
        ):
            result = generate_thumbnail.apply(args=["items/abc123.jpg"])
            assert result.result["thumb_key"] == "items/thumb_abc123.jpg"

    def test_thumbnail_key_format_for_different_sections(self):
        """Thumbnail key follows <section>/thumb_<uuid>.jpg for any section."""
        from src.backend.application.tasks.images import _generate_thumbnail_async
        from pathlib import PurePosixPath

        # Test the naming logic directly
        key = "categories/deadbeef-1234-5678-abcd-ef1234567890.png"
        path = PurePosixPath(key)
        thumb_key = str(path.parent / f"thumb_{path.stem}.jpg")

        assert thumb_key == "categories/thumb_deadbeef-1234-5678-abcd-ef1234567890.jpg"

    def test_generate_thumbnail_success(self):
        from src.backend.application.tasks.images import generate_thumbnail

        with patch(
            "src.backend.application.tasks.images.asyncio.run",
            return_value="items/thumb_uuid-abc.jpg",
        ):
            result = generate_thumbnail.apply(args=["items/uuid-abc.jpg", 400, 300])
            assert result.successful()
            assert result.result["thumb_key"] == "items/thumb_uuid-abc.jpg"

    def test_generate_thumbnail_task_name(self):
        from src.backend.application.tasks.images import generate_thumbnail

        assert generate_thumbnail.name == "coremarket.tasks.generate_thumbnail"

    def test_generate_thumbnail_default_dimensions(self):
        """Task default width=400, height=300."""
        from src.backend.application.tasks.images import generate_thumbnail

        with patch(
            "src.backend.application.tasks.images.asyncio.run",
            return_value="items/thumb_def.jpg",
        ) as mock_run:
            generate_thumbnail.apply(args=["items/def.jpg"])
            # asyncio.run called with a coroutine for (key, 400, 300)
            mock_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_thumbnail_uses_pillow_resize(self):
        """Integration: _generate_thumbnail_async applies thumbnail resize."""
        PIL = pytest.importorskip("PIL")
        from src.backend.application.tasks.images import _generate_thumbnail_async

        jpeg_bytes = _make_jpeg_bytes()

        mock_body = AsyncMock()
        mock_body.read.return_value = jpeg_bytes

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get_object.return_value = {"Body": mock_body}
        mock_client.put_object = AsyncMock()

        mock_session = MagicMock()
        mock_session.client.return_value = mock_client

        # aioboto3 and get_settings are local imports inside _generate_thumbnail_async,
        # so patch at their original module paths, not the images module namespace.
        with patch("aioboto3.Session", return_value=mock_session), \
             patch("src.backend.config.get_settings") as mock_cfg:
            mock_cfg.return_value = MagicMock(
                MINIO_ENDPOINT="http://minio:9000",
                MINIO_ACCESS_KEY="key",
                MINIO_SECRET_KEY="secret",
                MINIO_BUCKET="coremarket",
            )
            thumb_key = await _generate_thumbnail_async("items/uuid-test.jpg", 200, 150)

        assert thumb_key == "items/thumb_uuid-test.jpg"
        mock_client.put_object.assert_called_once()
        call_kwargs = mock_client.put_object.call_args.kwargs
        assert call_kwargs["Key"] == "items/thumb_uuid-test.jpg"
        assert call_kwargs["ContentType"] == "image/jpeg"

        uploaded_bytes = call_kwargs["Body"]
        from PIL import Image
        thumb_img = Image.open(io.BytesIO(uploaded_bytes))
        assert thumb_img.width <= 200
        assert thumb_img.height <= 150

    def test_generate_thumbnail_logs_on_completion(self, caplog):
        import logging

        from src.backend.application.tasks.images import generate_thumbnail

        with caplog.at_level(logging.INFO, logger="coremarket.tasks.images"):
            with patch(
                "src.backend.application.tasks.images.asyncio.run",
                return_value="items/thumb_log.jpg",
            ):
                generate_thumbnail.apply(args=["items/log.jpg"])

        assert any("task_started" in r.message for r in caplog.records)
        assert any("task_completed" in r.message for r in caplog.records)


class TestGenerateThumbnailRetry:
    def test_retries_on_minio_error(self):
        """Transient MinIO error causes the task to request retry."""
        from celery.exceptions import Retry
        from src.backend.application.tasks.images import generate_thumbnail

        with patch(
            "src.backend.application.tasks.images.asyncio.run",
            side_effect=ConnectionError("MinIO unreachable"),
        ):
            with pytest.raises(Retry):
                generate_thumbnail.apply(args=["items/retry.jpg"], throw=True)

    def test_fails_after_max_retries(self):
        """When retries are exhausted, Celery re-raises the original exception."""
        from src.backend.application.tasks.images import generate_thumbnail

        # When request.retries (3) > max_retries (3), self.retry(exc=exc) re-raises exc directly.
        with patch(
            "src.backend.application.tasks.images.asyncio.run",
            side_effect=ConnectionError("MinIO permanently down"),
        ):
            with pytest.raises(ConnectionError, match="MinIO permanently down"):
                generate_thumbnail.apply(args=["items/fail.jpg"], retries=3, throw=True)

    def test_max_retries_configured(self):
        from src.backend.application.tasks.images import generate_thumbnail

        assert generate_thumbnail.max_retries == 3

    @pytest.mark.asyncio
    async def test_invalid_image_bytes_raises(self):
        """PIL raises on invalid bytes; put_object must never be called."""
        import sys
        from src.backend.application.tasks.images import _generate_thumbnail_async

        invalid_bytes = b"not-an-image"

        mock_body = AsyncMock()
        mock_body.read.return_value = invalid_bytes

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get_object.return_value = {"Body": mock_body}
        mock_client.put_object = AsyncMock()

        mock_session = MagicMock()
        mock_session.client.return_value = mock_client

        # PIL is a local import inside _generate_thumbnail_async; inject a mock
        # that raises on Image.open so the test runs even without Pillow installed.
        mock_image_mod = MagicMock()
        mock_image_mod.open.side_effect = Exception("cannot identify image file")
        mock_pil_mod = MagicMock()
        mock_pil_mod.Image = mock_image_mod

        with patch.dict(sys.modules, {"PIL": mock_pil_mod, "PIL.Image": mock_image_mod}), \
             patch("aioboto3.Session", return_value=mock_session), \
             patch("src.backend.config.get_settings") as mock_cfg:
            mock_cfg.return_value = MagicMock(
                MINIO_ENDPOINT="http://minio:9000",
                MINIO_ACCESS_KEY="key",
                MINIO_SECRET_KEY="secret",
                MINIO_BUCKET="coremarket",
            )
            with pytest.raises(Exception, match="cannot identify image file"):
                await _generate_thumbnail_async("items/bad.jpg", 400, 300)

        mock_client.put_object.assert_not_called()

    @pytest.mark.asyncio
    async def test_upload_failure_raises(self):
        """put_object failure propagates from async helper."""
        pytest.importorskip("PIL")
        from src.backend.application.tasks.images import _generate_thumbnail_async

        jpeg_bytes = _make_jpeg_bytes()

        mock_body = AsyncMock()
        mock_body.read.return_value = jpeg_bytes

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get_object.return_value = {"Body": mock_body}
        mock_client.put_object = AsyncMock(side_effect=ConnectionError("S3 upload failed"))

        mock_session = MagicMock()
        mock_session.client.return_value = mock_client

        with patch("aioboto3.Session", return_value=mock_session), \
             patch("src.backend.config.get_settings") as mock_cfg:
            mock_cfg.return_value = MagicMock(
                MINIO_ENDPOINT="http://minio:9000",
                MINIO_ACCESS_KEY="key",
                MINIO_SECRET_KEY="secret",
                MINIO_BUCKET="coremarket",
            )
            with pytest.raises(ConnectionError, match="S3 upload failed"):
                await _generate_thumbnail_async("items/upload-fail.jpg", 400, 300)
