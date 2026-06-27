from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from src.backend.infrastructure.storage.minio.storage import MinIOFileStorage

_MODULE = "src.backend.infrastructure.storage.minio.storage"


def _mock_settings(endpoint="http://minio:9000", public_url="http://localhost:9000", bucket="coremarket"):
    settings = MagicMock()
    settings.MINIO_ENDPOINT = endpoint
    settings.MINIO_PUBLIC_URL = public_url
    settings.MINIO_BUCKET = bucket
    settings.MINIO_ACCESS_KEY = "minioadmin"
    settings.MINIO_SECRET_KEY = "minioadmin"
    return settings


def _make_s3_ctx(client: AsyncMock) -> MagicMock:
    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=client)
    ctx.__aexit__ = AsyncMock(return_value=None)
    return ctx


class TestMinIOFileStorageSave:

    async def test_save_returns_key_not_full_url(self):
        storage = MinIOFileStorage()
        client = AsyncMock()
        client.put_object = AsyncMock()

        with patch(f"{_MODULE}._session") as mock_session, \
             patch(f"{_MODULE}.get_settings", return_value=_mock_settings()):
            mock_session.client.return_value = _make_s3_ctx(client)
            result = await storage.save(b"data", "items", "jpg")

        assert result.startswith("items/")
        assert result.endswith(".jpg")
        assert "http" not in result
        assert "localhost" not in result

    async def test_save_calls_put_object_with_correct_bucket(self):
        storage = MinIOFileStorage()
        client = AsyncMock()
        client.put_object = AsyncMock()

        with patch(f"{_MODULE}._session") as mock_session, \
             patch(f"{_MODULE}.get_settings", return_value=_mock_settings()):
            mock_session.client.return_value = _make_s3_ctx(client)
            await storage.save(b"pixels", "categories", "png")

        client.put_object.assert_awaited_once()
        call_kwargs = client.put_object.call_args.kwargs
        assert call_kwargs["Bucket"] == "coremarket"
        assert call_kwargs["ContentType"] == "image/png"


class TestMinIOFileStorageGetPresignedUrl:

    async def test_replaces_internal_endpoint_with_public_url(self):
        storage = MinIOFileStorage()
        internal = "http://minio:9000/coremarket/items/uuid.jpg?X-Amz-Signature=abc"
        client = AsyncMock()
        client.generate_presigned_url = AsyncMock(return_value=internal)

        with patch(f"{_MODULE}._session") as mock_session, \
             patch(f"{_MODULE}.get_settings", return_value=_mock_settings()):
            mock_session.client.return_value = _make_s3_ctx(client)
            result = await storage.get_presigned_url("items/uuid.jpg", expires_in=3600)

        assert result == "http://localhost:9000/coremarket/items/uuid.jpg?X-Amz-Signature=abc"
        assert "minio:9000" not in result

    async def test_generate_presigned_url_called_with_correct_params(self):
        storage = MinIOFileStorage()
        client = AsyncMock()
        client.generate_presigned_url = AsyncMock(return_value="http://minio:9000/coremarket/k?sig=x")

        with patch(f"{_MODULE}._session") as mock_session, \
             patch(f"{_MODULE}.get_settings", return_value=_mock_settings()):
            mock_session.client.return_value = _make_s3_ctx(client)
            await storage.get_presigned_url("items/uuid.jpg", expires_in=7200)

        client.generate_presigned_url.assert_awaited_once_with(
            "get_object",
            Params={"Bucket": "coremarket", "Key": "items/uuid.jpg"},
            ExpiresIn=7200,
        )


class TestMinIOFileStorageGetPresignedUrls:

    async def test_returns_dict_keyed_by_input_keys(self):
        storage = MinIOFileStorage()
        keys = ["items/a.jpg", "items/b.jpg"]

        async def fake_single(key: str, expires_in: int = 3600) -> str:
            return f"http://localhost:9000/coremarket/{key}?sig=test"

        with patch.object(storage, "get_presigned_url", side_effect=fake_single):
            result = await storage.get_presigned_urls(keys)

        assert result == {
            "items/a.jpg": "http://localhost:9000/coremarket/items/a.jpg?sig=test",
            "items/b.jpg": "http://localhost:9000/coremarket/items/b.jpg?sig=test",
        }

    async def test_empty_list_returns_empty_dict(self):
        storage = MinIOFileStorage()

        async def fake_single(key: str, expires_in: int = 3600) -> str:
            return f"http://localhost/{key}"

        with patch.object(storage, "get_presigned_url", side_effect=fake_single):
            result = await storage.get_presigned_urls([])

        assert result == {}

    async def test_all_keys_returned_in_result(self):
        storage = MinIOFileStorage()
        keys = [f"items/{i}.jpg" for i in range(5)]

        async def fake_single(key: str, expires_in: int = 3600) -> str:
            return f"http://localhost/{key}"

        with patch.object(storage, "get_presigned_url", side_effect=fake_single):
            result = await storage.get_presigned_urls(keys)

        assert len(result) == 5
        assert set(result.keys()) == set(keys)
