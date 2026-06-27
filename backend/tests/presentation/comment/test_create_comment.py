from __future__ import annotations

from uuid import uuid4

ENDPOINT = "/api/v1/items/{item_id}/comments"


def _url(item_id=None):
    return ENDPOINT.format(item_id=item_id or uuid4())


async def test_create_comment_201(user_client, mock_create_uc):
    response = await user_client.post(_url(), json={"body": "Great product!"})
    assert response.status_code == 201
    data = response.json()
    assert data["body"] == "Great product!"
    assert data["is_deleted"] is False
    assert data["parent_id"] is None
    assert "id" in data
    assert "user_id" in data
    assert "children" in data


async def test_create_comment_201_with_parent(user_client, mock_create_uc):
    parent_id = str(uuid4())
    response = await user_client.post(_url(), json={"body": "Reply!", "parent_id": parent_id})
    assert response.status_code == 201
    cmd = mock_create_uc.execute.call_args[0][0]
    assert str(cmd.parent_id) == parent_id


async def test_create_comment_201_admin_can_comment(admin_client, mock_create_uc):
    response = await admin_client.post(_url(), json={"body": "Admin comment"})
    assert response.status_code == 201


async def test_create_comment_401_anon(anon_client):
    response = await anon_client.post(_url(), json={"body": "Hello"})
    assert response.status_code == 401


async def test_create_comment_422_missing_body(user_client, mock_create_uc):
    response = await user_client.post(_url(), json={})
    assert response.status_code == 422


async def test_create_comment_422_invalid_item_uuid(user_client, mock_create_uc):
    response = await user_client.post(ENDPOINT.format(item_id="not-a-uuid"), json={"body": "Hi"})
    assert response.status_code == 422
