from __future__ import annotations

import pytest
from unittest.mock import AsyncMock

from src.backend.application.storage.dtos.get_presigned_urls import GetPresignedUrlsResult
from src.backend.main import app
from src.backend.presentation.api.v1.storage.dependencies import get_presigned_urls_uc

_FAKE_URLS = {
    "items/test.jpg": "http://localhost:9000/coremarket/items/test.jpg?sig=abc123",
}


@pytest.fixture
def mock_storage_uc():
    uc = AsyncMock()
    uc.execute.return_value = GetPresignedUrlsResult(urls=_FAKE_URLS)
    app.dependency_overrides[get_presigned_urls_uc] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_presigned_urls_uc, None)
