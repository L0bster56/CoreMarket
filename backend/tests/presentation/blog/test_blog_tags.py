from __future__ import annotations

from uuid import uuid4

from src.backend.application.blog.dtos.blog_tags import ListBlogTagsResult
from src.backend.application.shared.errors import ConflictError, NotFoundError

BASE = "/api/v1/blog/tags"
_VALID_BODY = {"name": "Python", "slug": "python"}


async def test_list_tags_200(anon_client, mock_list_tags_uc):
    response = await anon_client.get(BASE)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["slug"] == "python"


async def test_list_tags_empty(anon_client, mock_list_tags_uc):
    mock_list_tags_uc.execute.return_value = ListBlogTagsResult(items=[])
    response = await anon_client.get(BASE)
    assert response.status_code == 200
    assert response.json() == []


async def test_create_tag_201(admin_client, mock_create_tag_uc):
    response = await admin_client.post(BASE, json=_VALID_BODY)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Python"
    assert data["slug"] == "python"
    assert "id" in data


async def test_create_tag_401_anon(anon_client, mock_create_tag_uc):
    response = await anon_client.post(BASE, json=_VALID_BODY)
    assert response.status_code == 401


async def test_create_tag_403_user(user_client, mock_create_tag_uc):
    response = await user_client.post(BASE, json=_VALID_BODY)
    assert response.status_code == 403


async def test_create_tag_409_conflict(admin_client, mock_create_tag_uc):
    mock_create_tag_uc.execute.side_effect = ConflictError("slug already exists")
    response = await admin_client.post(BASE, json=_VALID_BODY)
    assert response.status_code == 409


async def test_create_tag_422_missing_name(admin_client, mock_create_tag_uc):
    response = await admin_client.post(BASE, json={"slug": "python"})
    assert response.status_code == 422


async def test_create_tag_422_missing_slug(admin_client, mock_create_tag_uc):
    response = await admin_client.post(BASE, json={"name": "Python"})
    assert response.status_code == 422


async def test_update_tag_204(admin_client, mock_update_tag_uc):
    response = await admin_client.patch(f"{BASE}/{uuid4()}", json={"name": "Updated"})
    assert response.status_code == 204


async def test_update_tag_401_anon(anon_client, mock_update_tag_uc):
    response = await anon_client.patch(f"{BASE}/{uuid4()}", json={"name": "Updated"})
    assert response.status_code == 401


async def test_update_tag_403_user(user_client, mock_update_tag_uc):
    response = await user_client.patch(f"{BASE}/{uuid4()}", json={"name": "Updated"})
    assert response.status_code == 403


async def test_update_tag_404(admin_client, mock_update_tag_uc):
    mock_update_tag_uc.execute.side_effect = NotFoundError("not found")
    response = await admin_client.patch(f"{BASE}/{uuid4()}", json={"name": "Updated"})
    assert response.status_code == 404


async def test_update_tag_passes_fields_to_use_case(admin_client, mock_update_tag_uc):
    tag_id = uuid4()
    await admin_client.patch(f"{BASE}/{tag_id}", json={"name": "Science", "slug": "science"})
    cmd = mock_update_tag_uc.execute.call_args[0][0]
    assert cmd.tag_id == tag_id
    assert cmd.name == "Science"
    assert cmd.slug == "science"


async def test_delete_tag_204(admin_client, mock_delete_tag_uc):
    response = await admin_client.delete(f"{BASE}/{uuid4()}")
    assert response.status_code == 204


async def test_delete_tag_401_anon(anon_client, mock_delete_tag_uc):
    response = await anon_client.delete(f"{BASE}/{uuid4()}")
    assert response.status_code == 401


async def test_delete_tag_403_user(user_client, mock_delete_tag_uc):
    response = await user_client.delete(f"{BASE}/{uuid4()}")
    assert response.status_code == 403


async def test_delete_tag_404(admin_client, mock_delete_tag_uc):
    mock_delete_tag_uc.execute.side_effect = NotFoundError("not found")
    response = await admin_client.delete(f"{BASE}/{uuid4()}")
    assert response.status_code == 404


async def test_delete_tag_422_invalid_uuid(admin_client, mock_delete_tag_uc):
    response = await admin_client.delete(f"{BASE}/not-a-uuid")
    assert response.status_code == 422
