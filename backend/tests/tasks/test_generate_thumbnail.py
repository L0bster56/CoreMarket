"""Tests for generate_thumbnail Celery task.

Covers task-level behaviour and thumb-key naming.
Deep async/PIL tests (MinIO download, resize, upload) live in test_images.py.
"""
import io
import logging
from pathlib import PurePosixPath
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from celery.exceptions import Retry


def _make_jpeg_bytes() -> bytes:
    from PIL import Image

    img = Image.new("RGB", (800, 600), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


# ── Task configuration ─────────────────────────────────────────────────────────

class TestGenerateThumbnailConfig:
    def test_task_name(self):
        from src.backend.application.tasks.images import generate_thumbnail

        assert generate_thumbnail.name == "coremarket.tasks.generate_thumbnail"

    def test_max_retries(self):
        from src.backend.application.tasks.images import generate_thumbnail

        assert generate_thumbnail.max_retries == 3


# ── Success paths ──────────────────────────────────────────────────────────────

class TestGenerateThumbnailSuccess:
    def test_returns_thumb_key_dict(self):
        from src.backend.application.tasks.images import generate_thumbnail

        with patch(
            "src.backend.application.tasks.images.asyncio.run",
            return_value="items/thumb_abc123.jpg",
        ):
            result = generate_thumbnail.apply(args=["items/abc123.jpg"])

        assert result.result == {"thumb_key": "items/thumb_abc123.jpg"}

    def test_task_successful(self):
        from src.backend.application.tasks.images import generate_thumbnail

        with patch(
            "src.backend.application.tasks.images.asyncio.run",
            return_value="items/thumb_ok.jpg",
        ):
            result = generate_thumbnail.apply(args=["items/ok.jpg"])

        assert result.successful()

    def test_default_dimensions_passes_coroutine(self):
        from src.backend.application.tasks.images import generate_thumbnail

        with patch(
            "src.backend.application.tasks.images.asyncio.run",
            return_value="items/thumb_def.jpg",
        ) as mock_run:
            generate_thumbnail.apply(args=["items/def.jpg"])

        mock_run.assert_called_once()

    def test_custom_dimensions_accepted(self):
        from src.backend.application.tasks.images import generate_thumbnail

        with patch(
            "src.backend.application.tasks.images.asyncio.run",
            return_value="items/thumb_custom.jpg",
        ):
            result = generate_thumbnail.apply(args=["items/custom.jpg", 200, 150])

        assert result.result["thumb_key"] == "items/thumb_custom.jpg"

    def test_result_contains_only_thumb_key(self):
        from src.backend.application.tasks.images import generate_thumbnail

        with patch(
            "src.backend.application.tasks.images.asyncio.run",
            return_value="items/thumb_uuid.jpg",
        ):
            result = generate_thumbnail.apply(args=["items/uuid.jpg"])

        assert set(result.result.keys()) == {"thumb_key"}


# ── Thumb-key naming convention ────────────────────────────────────────────────

class TestThumbKeyNaming:
    """Verify the thumb_<stem>.jpg naming rule from PurePosixPath logic."""

    def _thumb(self, key: str) -> str:
        path = PurePosixPath(key)
        return str(path.parent / f"thumb_{path.stem}.jpg")

    def test_items_jpg(self):
        assert self._thumb("items/abc123.jpg") == "items/thumb_abc123.jpg"

    def test_categories_jpg(self):
        assert self._thumb("categories/cat-uuid.jpg") == "categories/thumb_cat-uuid.jpg"

    def test_nested_path(self):
        assert self._thumb("uploads/products/uuid-value.jpg") == "uploads/products/thumb_uuid-value.jpg"

    def test_png_source_becomes_jpg_thumb(self):
        result = self._thumb("items/deadbeef.png")
        assert result == "items/thumb_deadbeef.jpg"

    def test_thumb_prefix_in_result(self):
        result = self._thumb("items/some-uuid-1234.jpg")
        assert result.startswith("items/thumb_")
        assert result.endswith(".jpg")

    def test_stem_preserved(self):
        result = self._thumb("items/550e8400-e29b-41d4-a716-446655440000.jpg")
        assert "550e8400-e29b-41d4-a716-446655440000" in result


# ── Retry behaviour ────────────────────────────────────────────────────────────

class TestGenerateThumbnailRetry:
    def test_retries_on_minio_connection_error(self):
        from src.backend.application.tasks.images import generate_thumbnail

        with patch(
            "src.backend.application.tasks.images.asyncio.run",
            side_effect=ConnectionError("MinIO unreachable"),
        ):
            with pytest.raises(Retry):
                generate_thumbnail.apply(args=["items/retry.jpg"], throw=True)

    def test_retries_on_invalid_image(self):
        from src.backend.application.tasks.images import generate_thumbnail

        with patch(
            "src.backend.application.tasks.images.asyncio.run",
            side_effect=Exception("cannot identify image file"),
        ):
            with pytest.raises(Retry):
                generate_thumbnail.apply(args=["items/bad.jpg"], throw=True)

    def test_retries_on_upload_io_error(self):
        from src.backend.application.tasks.images import generate_thumbnail

        with patch(
            "src.backend.application.tasks.images.asyncio.run",
            side_effect=IOError("S3 write failed"),
        ):
            with pytest.raises(Retry):
                generate_thumbnail.apply(args=["items/upload-fail.jpg"], throw=True)

    def test_exhausted_retries_raises_original_exception(self):
        from src.backend.application.tasks.images import generate_thumbnail

        with patch(
            "src.backend.application.tasks.images.asyncio.run",
            side_effect=ConnectionError("MinIO permanently down"),
        ):
            with pytest.raises(ConnectionError, match="MinIO permanently down"):
                generate_thumbnail.apply(args=["items/fail.jpg"], retries=3, throw=True)


# ── Logging ────────────────────────────────────────────────────────────────────

class TestGenerateThumbnailLogging:
    def test_logs_task_started(self, caplog):
        from src.backend.application.tasks.images import generate_thumbnail

        with caplog.at_level(logging.INFO, logger="coremarket.tasks.images"):
            with patch(
                "src.backend.application.tasks.images.asyncio.run",
                return_value="items/thumb_log.jpg",
            ):
                generate_thumbnail.apply(args=["items/log.jpg"])

        assert any("task_started" in r.message for r in caplog.records)

    def test_logs_task_completed_on_success(self, caplog):
        from src.backend.application.tasks.images import generate_thumbnail

        with caplog.at_level(logging.INFO, logger="coremarket.tasks.images"):
            with patch(
                "src.backend.application.tasks.images.asyncio.run",
                return_value="items/thumb_log.jpg",
            ):
                generate_thumbnail.apply(args=["items/log.jpg"])

        assert any("task_completed" in r.message for r in caplog.records)

    def test_logs_task_failed_on_error(self, caplog):
        from src.backend.application.tasks.images import generate_thumbnail

        with caplog.at_level(logging.ERROR, logger="coremarket.tasks.images"):
            with patch(
                "src.backend.application.tasks.images.asyncio.run",
                side_effect=RuntimeError("oops"),
            ):
                try:
                    generate_thumbnail.apply(args=["items/fail-log.jpg"], throw=True)
                except Exception:
                    pass

        assert any("task_failed" in r.message for r in caplog.records)


# ── MinIO/PIL async helper ─────────────────────────────────────────────────────

class TestGenerateThumbnailAsync:
    """Direct tests of _generate_thumbnail_async with mocked aioboto3 + Pillow."""

    async def test_minio_download_called_with_correct_key(self):
        pytest.importorskip("PIL")
        from src.backend.application.tasks.images import _generate_thumbnail_async

        mock_body = AsyncMock()
        mock_body.read.return_value = _make_jpeg_bytes()

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get_object.return_value = {"Body": mock_body}
        mock_client.put_object = AsyncMock()

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
            await _generate_thumbnail_async("items/uuid-test.jpg", 400, 300)

        mock_client.get_object.assert_called_once_with(Bucket="coremarket", Key="items/uuid-test.jpg")

    async def test_minio_upload_correct_key_and_content_type(self):
        pytest.importorskip("PIL")
        from src.backend.application.tasks.images import _generate_thumbnail_async

        mock_body = AsyncMock()
        mock_body.read.return_value = _make_jpeg_bytes()

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get_object.return_value = {"Body": mock_body}
        mock_client.put_object = AsyncMock()

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
            thumb_key = await _generate_thumbnail_async("items/uuid-ct.jpg", 400, 300)

        assert thumb_key == "items/thumb_uuid-ct.jpg"
        call_kwargs = mock_client.put_object.call_args.kwargs
        assert call_kwargs["Key"] == "items/thumb_uuid-ct.jpg"
        assert call_kwargs["ContentType"] == "image/jpeg"
        assert call_kwargs["Bucket"] == "coremarket"

    async def test_resize_respects_dimensions(self):
        pytest.importorskip("PIL")
        from src.backend.application.tasks.images import _generate_thumbnail_async

        mock_body = AsyncMock()
        mock_body.read.return_value = _make_jpeg_bytes()  # 800×600 source

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get_object.return_value = {"Body": mock_body}
        mock_client.put_object = AsyncMock()

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
            await _generate_thumbnail_async("items/resize-test.jpg", 200, 150)

        uploaded_bytes = mock_client.put_object.call_args.kwargs["Body"]
        from PIL import Image

        thumb = Image.open(io.BytesIO(uploaded_bytes))
        assert thumb.width <= 200
        assert thumb.height <= 150

    async def test_invalid_image_does_not_upload(self):
        """PIL exception on bad bytes must prevent upload."""
        import sys
        from src.backend.application.tasks.images import _generate_thumbnail_async

        mock_body = AsyncMock()
        mock_body.read.return_value = b"definitely-not-an-image"

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get_object.return_value = {"Body": mock_body}
        mock_client.put_object = AsyncMock()

        mock_session = MagicMock()
        mock_session.client.return_value = mock_client

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

    async def test_upload_failure_propagates(self):
        pytest.importorskip("PIL")
        from src.backend.application.tasks.images import _generate_thumbnail_async

        mock_body = AsyncMock()
        mock_body.read.return_value = _make_jpeg_bytes()

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
