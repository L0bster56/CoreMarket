from __future__ import annotations

from unittest.mock import AsyncMock, patch

ENDPOINT = "/api/v1/upload"
_PATCH_TARGET = "src.backend.presentation.api.v1.upload.router.UploadImageUseCase"
_FAKE_FILE = ("test.jpg", b"fake image data", "image/jpeg")


async def test_upload_201(admin_client):
    with patch(_PATCH_TARGET) as MockUC:
        MockUC.return_value.execute = AsyncMock(return_value="items/abc123.jpg")
        files = {"file": _FAKE_FILE}
        response = await admin_client.post(f"{ENDPOINT}?section=items", files=files)
    assert response.status_code == 201
    assert response.json()["key"] == "items/abc123.jpg"


async def test_upload_201_section_categories(admin_client):
    with patch(_PATCH_TARGET) as MockUC:
        MockUC.return_value.execute = AsyncMock(return_value="categories/img.jpg")
        files = {"file": _FAKE_FILE}
        response = await admin_client.post(f"{ENDPOINT}?section=categories", files=files)
    assert response.status_code == 201


async def test_upload_201_section_users(admin_client):
    with patch(_PATCH_TARGET) as MockUC:
        MockUC.return_value.execute = AsyncMock(return_value="users/avatar.jpg")
        files = {"file": _FAKE_FILE}
        response = await admin_client.post(f"{ENDPOINT}?section=users", files=files)
    assert response.status_code == 201


async def test_upload_400_invalid_section(admin_client):
    with patch(_PATCH_TARGET) as MockUC:
        MockUC.return_value.execute = AsyncMock(return_value="/media/items/img.jpg")
        files = {"file": _FAKE_FILE}
        response = await admin_client.post(f"{ENDPOINT}?section=invalid", files=files)
    assert response.status_code == 400


async def test_upload_403_regular_user(user_client):
    files = {"file": _FAKE_FILE}
    response = await user_client.post(f"{ENDPOINT}?section=items", files=files)
    assert response.status_code == 403


async def test_upload_401_anon(anon_client):
    files = {"file": _FAKE_FILE}
    response = await anon_client.post(f"{ENDPOINT}?section=items", files=files)
    assert response.status_code == 401


async def test_upload_422_missing_file(admin_client):
    response = await admin_client.post(f"{ENDPOINT}?section=items")
    assert response.status_code == 422


async def test_upload_422_missing_section(admin_client):
    files = {"file": _FAKE_FILE}
    response = await admin_client.post(ENDPOINT, files=files)
    assert response.status_code == 422
