from __future__ import annotations

ENDPOINT = "/api/v1/auth/login"
_VALID = {"username": "testuser", "password": "ValidPass1"}


async def test_login_200(public_client):
    response = await public_client.post(ENDPOINT, json=_VALID)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "Bearer"


async def test_login_401_user_not_found(public_client, mock_uow):
    mock_uow.users.get_by_username.return_value = None
    response = await public_client.post(ENDPOINT, json=_VALID)
    assert response.status_code == 401


async def test_login_401_wrong_password(public_client, mock_hasher):
    mock_hasher.verify.return_value = False
    response = await public_client.post(ENDPOINT, json=_VALID)
    assert response.status_code == 401


async def test_login_422_missing_password(public_client):
    response = await public_client.post(ENDPOINT, json={"username": "testuser"})
    assert response.status_code == 422


async def test_login_422_missing_username(public_client):
    response = await public_client.post(ENDPOINT, json={"password": "ValidPass1"})
    assert response.status_code == 422
