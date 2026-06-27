from __future__ import annotations

import pytest
from unittest.mock import AsyncMock

from src.backend.application.shared.errors import BadRequestError
from src.backend.application.storage.dtos.get_presigned_urls import GetPresignedUrlsCommand
from src.backend.application.storage.use_cases.get_presigned_urls import GetPresignedUrlsUseCase


class TestGetPresignedUrlsUseCase:

    async def test_returns_urls_for_valid_keys(self):
        mock_storage = AsyncMock()
        mock_storage.get_presigned_urls.return_value = {
            "items/a.jpg": "http://localhost:9000/coremarket/items/a.jpg?sig=x",
        }
        uc = GetPresignedUrlsUseCase(storage=mock_storage)

        result = await uc.execute(GetPresignedUrlsCommand(keys=["items/a.jpg"]))

        assert result.urls == {"items/a.jpg": "http://localhost:9000/coremarket/items/a.jpg?sig=x"}

    async def test_raises_bad_request_when_101_keys(self):
        mock_storage = AsyncMock()
        uc = GetPresignedUrlsUseCase(storage=mock_storage)

        with pytest.raises(BadRequestError):
            await uc.execute(GetPresignedUrlsCommand(keys=["key"] * 101))

        mock_storage.get_presigned_urls.assert_not_called()

    async def test_accepts_exactly_100_keys(self):
        keys = [f"items/{i}.jpg" for i in range(100)]
        mock_storage = AsyncMock()
        mock_storage.get_presigned_urls.return_value = {k: f"http://url/{k}" for k in keys}
        uc = GetPresignedUrlsUseCase(storage=mock_storage)

        result = await uc.execute(GetPresignedUrlsCommand(keys=keys))

        assert len(result.urls) == 100
        mock_storage.get_presigned_urls.assert_called_once()

    async def test_empty_keys_returns_empty_dict(self):
        mock_storage = AsyncMock()
        mock_storage.get_presigned_urls.return_value = {}
        uc = GetPresignedUrlsUseCase(storage=mock_storage)

        result = await uc.execute(GetPresignedUrlsCommand(keys=[]))

        assert result.urls == {}

    async def test_passes_expires_in_to_storage(self):
        mock_storage = AsyncMock()
        mock_storage.get_presigned_urls.return_value = {}
        uc = GetPresignedUrlsUseCase(storage=mock_storage)

        await uc.execute(GetPresignedUrlsCommand(keys=[], expires_in=7200))

        mock_storage.get_presigned_urls.assert_called_once_with([], 7200)

    async def test_error_message_contains_limit(self):
        mock_storage = AsyncMock()
        uc = GetPresignedUrlsUseCase(storage=mock_storage)

        with pytest.raises(BadRequestError, match="100"):
            await uc.execute(GetPresignedUrlsCommand(keys=["k"] * 101))
