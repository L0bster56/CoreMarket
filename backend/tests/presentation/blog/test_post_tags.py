from __future__ import annotations

from uuid import uuid4

from src.backend.application.shared.errors import NotFoundError

BASE = "/api/v1/blog/posts"


async def test_add_tag_204(admin_client, mock_add_tag_uc):
    tag_id = uuid4()
    response = await admin_client.post(f"{BASE}/test-post/tags", json={"tag_id": str(tag_id)})
    assert response.status_code == 204


async def test_add_tag_401_anon(anon_client, mock_add_tag_uc):
    response = await anon_client.post(f"{BASE}/test-post/tags", json={"tag_id": str(uuid4())})
    assert response.status_code == 401


async def test_add_tag_403_user(user_client, mock_add_tag_uc):
    response = await user_client.post(f"{BASE}/test-post/tags", json={"tag_id": str(uuid4())})
    assert response.status_code == 403


async def test_add_tag_404_post_not_found(admin_client, mock_add_tag_uc):
    mock_add_tag_uc.execute.side_effect = NotFoundError("post not found")
    response = await admin_client.post(f"{BASE}/missing/tags", json={"tag_id": str(uuid4())})
    assert response.status_code == 404


async def test_add_tag_422_invalid_uuid(admin_client, mock_add_tag_uc):
    response = await admin_client.post(f"{BASE}/test-post/tags", json={"tag_id": "not-a-uuid"})
    assert response.status_code == 422


async def test_add_tag_passes_fields_to_use_case(admin_client, mock_add_tag_uc):
    tag_id = uuid4()
    await admin_client.post(f"{BASE}/my-slug/tags", json={"tag_id": str(tag_id)})
    cmd = mock_add_tag_uc.execute.call_args[0][0]
    assert cmd.slug == "my-slug"
    assert cmd.tag_id == tag_id


async def test_remove_tag_204(admin_client, mock_remove_tag_uc):
    response = await admin_client.delete(f"{BASE}/test-post/tags/{uuid4()}")
    assert response.status_code == 204


async def test_remove_tag_401_anon(anon_client, mock_remove_tag_uc):
    response = await anon_client.delete(f"{BASE}/test-post/tags/{uuid4()}")
    assert response.status_code == 401


async def test_remove_tag_403_user(user_client, mock_remove_tag_uc):
    response = await user_client.delete(f"{BASE}/test-post/tags/{uuid4()}")
    assert response.status_code == 403


async def test_remove_tag_404(admin_client, mock_remove_tag_uc):
    mock_remove_tag_uc.execute.side_effect = NotFoundError("not found")
    response = await admin_client.delete(f"{BASE}/missing/tags/{uuid4()}")
    assert response.status_code == 404
