from __future__ import annotations

from uuid import uuid4

from src.backend.application.shared.errors import NotAuthorizedError, NotFoundError

ENDPOINT = "/api/v1/items/{item_id}/comments/{comment_id}"


def _url(item_id=None, comment_id=None):
    return ENDPOINT.format(item_id=item_id or uuid4(), comment_id=comment_id or uuid4())


async def test_update_comment_204(user_client, mock_update_uc):
    response = await user_client.patch(_url(), json={"body": "Updated text"})
    assert response.status_code == 204


async def test_update_comment_204_admin(admin_client, mock_update_uc):
    response = await admin_client.patch(_url(), json={"body": "Admin updated"})
    assert response.status_code == 204


async def test_update_comment_404(user_client, mock_update_uc):
    mock_update_uc.execute.side_effect = NotFoundError("comment not found")
    response = await user_client.patch(_url(), json={"body": "Updated"})
    assert response.status_code == 404


async def test_update_comment_401_not_owner(user_client, mock_update_uc):
    mock_update_uc.execute.side_effect = NotAuthorizedError("not owner")
    response = await user_client.patch(_url(), json={"body": "Updated"})
    assert response.status_code == 401


async def test_update_comment_401_anon(anon_client):
    response = await anon_client.patch(_url(), json={"body": "Updated"})
    assert response.status_code == 401


async def test_update_comment_422_missing_body(user_client, mock_update_uc):
    response = await user_client.patch(_url(), json={})
    assert response.status_code == 422


async def test_update_comment_422_invalid_uuid(user_client, mock_update_uc):
    response = await user_client.patch(
        ENDPOINT.format(item_id=uuid4(), comment_id="not-a-uuid"),
        json={"body": "X"},
    )
    assert response.status_code == 422
