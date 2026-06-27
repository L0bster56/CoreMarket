from __future__ import annotations

from uuid import uuid4

from src.backend.application.shared.errors import NotFoundError

ENDPOINT = "/api/v1/users"


async def test_get_user_200(admin_client, mock_get_uc):
    response = await admin_client.get(f"{ENDPOINT}/{uuid4()}")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "targetuser"
    assert data["email"] == "target@example.com"
    assert "id" in data
    assert "role" in data
    assert "created_at" in data


async def test_get_user_404(admin_client, mock_get_uc):
    mock_get_uc.execute.side_effect = NotFoundError("user not found")
    response = await admin_client.get(f"{ENDPOINT}/{uuid4()}")
    assert response.status_code == 404


async def test_get_user_403_regular_user(user_client, mock_get_uc):
    response = await user_client.get(f"{ENDPOINT}/{uuid4()}")
    assert response.status_code == 403


async def test_get_user_401_anon(anon_client, mock_get_uc):
    response = await anon_client.get(f"{ENDPOINT}/{uuid4()}")
    assert response.status_code == 401


async def test_get_user_422_invalid_uuid(admin_client, mock_get_uc):
    response = await admin_client.get(f"{ENDPOINT}/not-a-uuid")
    assert response.status_code == 422
