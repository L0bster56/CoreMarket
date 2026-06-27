from __future__ import annotations

from unittest.mock import MagicMock
from uuid import uuid4

from src.backend.application.shared.errors import NotFoundError

ENDPOINT = "/api/v1/items/{item_id}/rating"


def _url(item_id=None):
    return ENDPOINT.format(item_id=item_id or uuid4())


async def test_get_rating_200_anon(
    anon_client, mock_get_uc, mock_optional_user_none, mock_rating_repo
):
    response = await anon_client.get(_url())
    assert response.status_code == 200
    data = response.json()
    assert data["average"] == 4.2
    assert data["count"] == 15
    assert data["user_score"] is None


async def test_get_rating_200_authenticated_no_rating(
    user_client, mock_get_uc, mock_optional_user_authenticated, mock_rating_repo
):
    mock_rating_repo.get_by_item_and_user.return_value = None
    response = await user_client.get(_url())
    assert response.status_code == 200
    data = response.json()
    assert data["average"] == 4.2
    assert data["user_score"] is None


async def test_get_rating_200_authenticated_with_rating(
    user_client, mock_get_uc, mock_optional_user_authenticated, mock_rating_repo
):
    mock_rating = MagicMock()
    mock_rating.score.value = 4
    mock_rating_repo.get_by_item_and_user.return_value = mock_rating
    response = await user_client.get(_url())
    assert response.status_code == 200
    data = response.json()
    assert data["user_score"] == 4


async def test_get_rating_404(
    anon_client, mock_get_uc, mock_optional_user_none, mock_rating_repo
):
    mock_get_uc.execute.side_effect = NotFoundError("item not found")
    response = await anon_client.get(_url())
    assert response.status_code == 404


async def test_get_rating_422_invalid_uuid(
    anon_client, mock_get_uc, mock_optional_user_none, mock_rating_repo
):
    response = await anon_client.get(ENDPOINT.format(item_id="not-a-uuid"))
    assert response.status_code == 422
