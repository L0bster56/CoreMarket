from __future__ import annotations

from uuid import uuid4

from src.backend.application.shared.errors import NotFoundError

ENDPOINT = "/api/v1/categories"


async def test_update_category_204(admin_client, mock_update_uc):
    response = await admin_client.patch(f"{ENDPOINT}/{uuid4()}", json={"name": "Updated"})
    assert response.status_code == 204


async def test_update_category_204_no_fields(admin_client, mock_update_uc):
    response = await admin_client.patch(f"{ENDPOINT}/{uuid4()}", json={})
    assert response.status_code == 204


async def test_update_category_404(admin_client, mock_update_uc):
    mock_update_uc.execute.side_effect = NotFoundError("category not found")
    response = await admin_client.patch(f"{ENDPOINT}/{uuid4()}", json={"name": "X"})
    assert response.status_code == 404


async def test_update_category_403_regular_user(user_client, mock_update_uc):
    response = await user_client.patch(f"{ENDPOINT}/{uuid4()}", json={"name": "X"})
    assert response.status_code == 403


async def test_update_category_401_anon(anon_client, mock_update_uc):
    response = await anon_client.patch(f"{ENDPOINT}/{uuid4()}", json={"name": "X"})
    assert response.status_code == 401


async def test_update_category_422_invalid_uuid(admin_client, mock_update_uc):
    response = await admin_client.patch(f"{ENDPOINT}/not-a-uuid", json={"name": "X"})
    assert response.status_code == 422
