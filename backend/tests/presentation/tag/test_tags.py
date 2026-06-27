from __future__ import annotations

from uuid import uuid4

from src.backend.application.shared.errors import ConflictError, NotFoundError
from src.backend.application.tag.dtos.list_tags import ListTagsResult

BASE = "/api/v1/tags"
_VALID_BODY = {"name": "Python", "slug": "python"}


# --- GET /tags ---

async def test_list_tags_200(anon_client, mock_list_uc):
    response = await anon_client.get(BASE)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["slug"] == "python"
    assert data[1]["slug"] == "django"


async def test_list_tags_empty(anon_client, mock_list_uc):
    mock_list_uc.execute.return_value = ListTagsResult(items=[])
    response = await anon_client.get(BASE)
    assert response.status_code == 200
    assert response.json() == []


# --- POST /tags ---

async def test_create_tag_201(admin_client, mock_create_uc):
    response = await admin_client.post(BASE, json=_VALID_BODY)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Python"
    assert data["slug"] == "python"
    assert "id" in data


async def test_create_tag_403_regular_user(user_client, mock_create_uc):
    response = await user_client.post(BASE, json=_VALID_BODY)
    assert response.status_code == 403


async def test_create_tag_401_anon(anon_client, mock_create_uc):
    response = await anon_client.post(BASE, json=_VALID_BODY)
    assert response.status_code == 401


async def test_create_tag_409_conflict(admin_client, mock_create_uc):
    mock_create_uc.execute.side_effect = ConflictError("slug already exists")
    response = await admin_client.post(BASE, json=_VALID_BODY)
    assert response.status_code == 409


async def test_create_tag_422_missing_slug(admin_client, mock_create_uc):
    response = await admin_client.post(BASE, json={"name": "Python"})
    assert response.status_code == 422


async def test_create_tag_422_missing_name(admin_client, mock_create_uc):
    response = await admin_client.post(BASE, json={"slug": "python"})
    assert response.status_code == 422


# --- DELETE /tags/{tag_id} ---

async def test_delete_tag_204(admin_client, mock_delete_uc):
    response = await admin_client.delete(f"{BASE}/{uuid4()}")
    assert response.status_code == 204


async def test_delete_tag_404(admin_client, mock_delete_uc):
    mock_delete_uc.execute.side_effect = NotFoundError("tag not found")
    response = await admin_client.delete(f"{BASE}/{uuid4()}")
    assert response.status_code == 404


async def test_delete_tag_403_regular_user(user_client, mock_delete_uc):
    response = await user_client.delete(f"{BASE}/{uuid4()}")
    assert response.status_code == 403


async def test_delete_tag_401_anon(anon_client, mock_delete_uc):
    response = await anon_client.delete(f"{BASE}/{uuid4()}")
    assert response.status_code == 401


async def test_delete_tag_422_invalid_uuid(admin_client, mock_delete_uc):
    response = await admin_client.delete(f"{BASE}/not-a-uuid")
    assert response.status_code == 422
