from __future__ import annotations

from uuid import uuid4

from src.backend.application.shared.errors import NotFoundError

ENDPOINT = "/api/v1/items/{item_id}/rating"


def _url(item_id=None):
    return ENDPOINT.format(item_id=item_id or uuid4())


async def test_update_rating_204(user_client, mock_update_uc):
    response = await user_client.patch(_url(), json={"score": 3})
    assert response.status_code == 204


async def test_update_rating_204_admin(admin_client, mock_update_uc):
    response = await admin_client.patch(_url(), json={"score": 5})
    assert response.status_code == 204


async def test_update_rating_404(user_client, mock_update_uc):
    mock_update_uc.execute.side_effect = NotFoundError("rating not found")
    response = await user_client.patch(_url(), json={"score": 3})
    assert response.status_code == 404


async def test_update_rating_401_anon(anon_client):
    response = await anon_client.patch(_url(), json={"score": 3})
    assert response.status_code == 401


async def test_update_rating_422_score_too_low(user_client, mock_update_uc):
    response = await user_client.patch(_url(), json={"score": 0})
    assert response.status_code == 422


async def test_update_rating_422_score_too_high(user_client, mock_update_uc):
    response = await user_client.patch(_url(), json={"score": 6})
    assert response.status_code == 422


async def test_update_rating_422_missing_score(user_client, mock_update_uc):
    response = await user_client.patch(_url(), json={})
    assert response.status_code == 422


async def test_update_rating_422_invalid_uuid(user_client, mock_update_uc):
    response = await user_client.patch(ENDPOINT.format(item_id="not-a-uuid"), json={"score": 3})
    assert response.status_code == 422
