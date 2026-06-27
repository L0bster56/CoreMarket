from __future__ import annotations

from uuid import uuid4

from src.backend.application.shared.errors import NotFoundError

ENDPOINT = "/api/v1/users"


async def test_delete_user_204(admin_client, mock_delete_uc):
    response = await admin_client.delete(f"{ENDPOINT}/{uuid4()}")
    assert response.status_code == 204


async def test_delete_user_404(admin_client, mock_delete_uc):
    mock_delete_uc.execute.side_effect = NotFoundError("user not found")
    response = await admin_client.delete(f"{ENDPOINT}/{uuid4()}")
    assert response.status_code == 404


async def test_delete_user_403_regular_user(user_client, mock_delete_uc):
    response = await user_client.delete(f"{ENDPOINT}/{uuid4()}")
    assert response.status_code == 403


async def test_delete_user_401_anon(anon_client, mock_delete_uc):
    response = await anon_client.delete(f"{ENDPOINT}/{uuid4()}")
    assert response.status_code == 401


async def test_delete_user_422_invalid_uuid(admin_client, mock_delete_uc):
    response = await admin_client.delete(f"{ENDPOINT}/not-a-uuid")
    assert response.status_code == 422
