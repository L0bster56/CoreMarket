from __future__ import annotations

from uuid import uuid4

from src.backend.application.shared.errors import NotFoundError

ENDPOINT = "/api/v1/items/{item_id}/rating"


def _url(item_id=None):
    return ENDPOINT.format(item_id=item_id or uuid4())


async def test_delete_rating_204(user_client, mock_delete_uc):
    response = await user_client.delete(_url())
    assert response.status_code == 204


async def test_delete_rating_204_admin(admin_client, mock_delete_uc):
    response = await admin_client.delete(_url())
    assert response.status_code == 204


async def test_delete_rating_404(user_client, mock_delete_uc):
    mock_delete_uc.execute.side_effect = NotFoundError("rating not found")
    response = await user_client.delete(_url())
    assert response.status_code == 404


async def test_delete_rating_401_anon(anon_client):
    response = await anon_client.delete(_url())
    assert response.status_code == 401


async def test_delete_rating_422_invalid_uuid(user_client, mock_delete_uc):
    response = await user_client.delete(ENDPOINT.format(item_id="not-a-uuid"))
    assert response.status_code == 422
