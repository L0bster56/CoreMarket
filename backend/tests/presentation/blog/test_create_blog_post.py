from __future__ import annotations

from src.backend.application.shared.errors import ConflictError

ENDPOINT = "/api/v1/blog/posts"
_VALID = {"title": "Hello World", "slug": "hello-world"}


async def test_create_post_201_admin(admin_client, mock_create_post_uc, mock_get_post_uc):
    response = await admin_client.post(ENDPOINT, json=_VALID)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "slug" in data
    assert "title" in data


async def test_create_post_403_regular_user(user_client, mock_create_post_uc, mock_get_post_uc):
    response = await user_client.post(ENDPOINT, json=_VALID)
    assert response.status_code == 403


async def test_create_post_401_anon(anon_client, mock_create_post_uc, mock_get_post_uc):
    response = await anon_client.post(ENDPOINT, json=_VALID)
    assert response.status_code == 401


async def test_create_post_409_slug_conflict(admin_client, mock_create_post_uc, mock_get_post_uc):
    mock_create_post_uc.execute.side_effect = ConflictError("slug already exists")
    response = await admin_client.post(ENDPOINT, json=_VALID)
    assert response.status_code == 409


async def test_create_post_422_missing_title(admin_client, mock_create_post_uc, mock_get_post_uc):
    response = await admin_client.post(ENDPOINT, json={"slug": "hello-world"})
    assert response.status_code == 422


async def test_create_post_422_missing_slug(admin_client, mock_create_post_uc, mock_get_post_uc):
    response = await admin_client.post(ENDPOINT, json={"title": "Hello World"})
    assert response.status_code == 422


async def test_create_post_with_optional_short_description(
    admin_client, mock_create_post_uc, mock_get_post_uc
):
    payload = {**_VALID, "short_description": "A brief summary"}
    response = await admin_client.post(ENDPOINT, json=payload)
    assert response.status_code == 201
