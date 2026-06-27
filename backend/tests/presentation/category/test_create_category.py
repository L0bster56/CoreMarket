from __future__ import annotations

from src.backend.application.shared.errors import ConflictError

ENDPOINT = "/api/v1/categories"
_VALID = {"name": "Electronics", "slug": "electronics"}


async def test_create_category_201(admin_client, mock_create_uc):
    response = await admin_client.post(ENDPOINT, json=_VALID)
    assert response.status_code == 201
    data = response.json()
    assert data["slug"] == "electronics"
    assert data["name"] == "Electronics"
    assert "id" in data
    assert "created_at" in data


async def test_create_category_403_regular_user(user_client, mock_create_uc):
    response = await user_client.post(ENDPOINT, json=_VALID)
    assert response.status_code == 403


async def test_create_category_401_anon(anon_client, mock_create_uc):
    response = await anon_client.post(ENDPOINT, json=_VALID)
    assert response.status_code == 401


async def test_create_category_409_conflict(admin_client, mock_create_uc):
    mock_create_uc.execute.side_effect = ConflictError("slug already exists")
    response = await admin_client.post(ENDPOINT, json=_VALID)
    assert response.status_code == 409


async def test_create_category_422_missing_slug(admin_client, mock_create_uc):
    response = await admin_client.post(ENDPOINT, json={"name": "Electronics"})
    assert response.status_code == 422


async def test_create_category_422_missing_name(admin_client, mock_create_uc):
    response = await admin_client.post(ENDPOINT, json={"slug": "electronics"})
    assert response.status_code == 422
