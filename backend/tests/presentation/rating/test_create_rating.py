from __future__ import annotations

from uuid import uuid4

from src.backend.application.shared.errors import ConflictError

ENDPOINT = "/api/v1/items/{item_id}/rating"


def _url(item_id=None):
    return ENDPOINT.format(item_id=item_id or uuid4())


async def test_create_rating_201(user_client, mock_create_uc, mock_rating_repo):
    response = await user_client.post(_url(), json={"score": 4})
    assert response.status_code == 201
    data = response.json()
    assert data["average"] == 4.2
    assert data["count"] == 15
    assert data["user_score"] == 4


async def test_create_rating_201_score_min(user_client, mock_create_uc, mock_rating_repo):
    response = await user_client.post(_url(), json={"score": 1})
    assert response.status_code == 201
    assert response.json()["user_score"] == 1


async def test_create_rating_201_score_max(user_client, mock_create_uc, mock_rating_repo):
    response = await user_client.post(_url(), json={"score": 5})
    assert response.status_code == 201
    assert response.json()["user_score"] == 5


async def test_create_rating_401_anon(anon_client, mock_rating_repo):
    # mock_rating_repo only — let auth dep fire for 401
    response = await anon_client.post(_url(), json={"score": 4})
    assert response.status_code == 401


async def test_create_rating_409_conflict(user_client, mock_create_uc, mock_rating_repo):
    mock_create_uc.execute.side_effect = ConflictError("already rated")
    response = await user_client.post(_url(), json={"score": 4})
    assert response.status_code == 409


async def test_create_rating_422_score_too_low(user_client, mock_create_uc, mock_rating_repo):
    response = await user_client.post(_url(), json={"score": 0})
    assert response.status_code == 422


async def test_create_rating_422_score_too_high(user_client, mock_create_uc, mock_rating_repo):
    response = await user_client.post(_url(), json={"score": 6})
    assert response.status_code == 422


async def test_create_rating_422_missing_score(user_client, mock_create_uc, mock_rating_repo):
    response = await user_client.post(_url(), json={})
    assert response.status_code == 422
