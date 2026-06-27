from __future__ import annotations

from uuid import uuid4

from src.backend.application.shared.errors import NotFoundError

ENDPOINT = "/api/v1/items"

_VALID_GALLERY = {"image_url": "/media/items/photo.jpg"}


async def test_add_gallery_image_201(admin_client, mock_add_gallery_uc):
    response = await admin_client.post(f"{ENDPOINT}/{uuid4()}/gallery", json=_VALID_GALLERY)
    assert response.status_code == 201
    data = response.json()
    assert data["image_url"] == "/media/items/test.jpg"
    assert "id" in data


async def test_add_gallery_image_404(admin_client, mock_add_gallery_uc):
    mock_add_gallery_uc.execute.side_effect = NotFoundError("item not found")
    response = await admin_client.post(f"{ENDPOINT}/{uuid4()}/gallery", json=_VALID_GALLERY)
    assert response.status_code == 404


async def test_add_gallery_image_403_regular_user(user_client, mock_add_gallery_uc):
    response = await user_client.post(f"{ENDPOINT}/{uuid4()}/gallery", json=_VALID_GALLERY)
    assert response.status_code == 403


async def test_add_gallery_image_401_anon(anon_client, mock_add_gallery_uc):
    response = await anon_client.post(f"{ENDPOINT}/{uuid4()}/gallery", json=_VALID_GALLERY)
    assert response.status_code == 401


async def test_add_gallery_image_422_missing_image_url(admin_client, mock_add_gallery_uc):
    response = await admin_client.post(f"{ENDPOINT}/{uuid4()}/gallery", json={})
    assert response.status_code == 422


async def test_delete_gallery_image_204(admin_client, mock_delete_gallery_uc):
    response = await admin_client.delete(f"{ENDPOINT}/{uuid4()}/gallery/{uuid4()}")
    assert response.status_code == 204


async def test_delete_gallery_image_404(admin_client, mock_delete_gallery_uc):
    mock_delete_gallery_uc.execute.side_effect = NotFoundError("image not found")
    response = await admin_client.delete(f"{ENDPOINT}/{uuid4()}/gallery/{uuid4()}")
    assert response.status_code == 404


async def test_delete_gallery_image_403_regular_user(user_client, mock_delete_gallery_uc):
    response = await user_client.delete(f"{ENDPOINT}/{uuid4()}/gallery/{uuid4()}")
    assert response.status_code == 403


async def test_delete_gallery_image_401_anon(anon_client, mock_delete_gallery_uc):
    response = await anon_client.delete(f"{ENDPOINT}/{uuid4()}/gallery/{uuid4()}")
    assert response.status_code == 401
