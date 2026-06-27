from __future__ import annotations

_GET_ME = "/api/v1/auth/me"
_UPDATE_ME = "/api/v1/auth/me"
_LOGOUT = "/api/v1/auth/logout"
_CHANGE_PASS = "/api/v1/auth/change-password"
_REFRESH = "/api/v1/auth/refresh"


# --- GET /me ---

async def test_get_me_200(logged_in_client):
    response = await logged_in_client.get(_GET_ME)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "password" not in data


async def test_get_me_401_no_token(public_client):
    response = await public_client.get(_GET_ME)
    assert response.status_code == 401


# --- POST /logout ---

async def test_logout_204(logged_in_client):
    response = await logged_in_client.post(_LOGOUT)
    assert response.status_code == 204


async def test_logout_401_no_token(public_client):
    response = await public_client.post(_LOGOUT)
    assert response.status_code == 401


# --- POST /refresh ---

async def test_refresh_200(public_client):
    response = await public_client.post(_REFRESH, json={"refresh_token": "some_refresh_token"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "Bearer"


async def test_refresh_422_missing_token(public_client):
    response = await public_client.post(_REFRESH, json={})
    assert response.status_code == 422


# --- PATCH /me ---

async def test_update_me_200(logged_in_client):
    response = await logged_in_client.patch(_UPDATE_ME, json={"username": "newname"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newname"


async def test_update_me_200_no_changes(logged_in_client):
    response = await logged_in_client.patch(_UPDATE_ME, json={})
    assert response.status_code == 200


async def test_update_me_409_username_conflict(logged_in_client, mock_uow):
    mock_uow.users.exists_username.return_value = True
    response = await logged_in_client.patch(_UPDATE_ME, json={"username": "taken"})
    assert response.status_code == 409


async def test_update_me_401_no_token(public_client):
    response = await public_client.patch(_UPDATE_ME, json={"username": "newname"})
    assert response.status_code == 401


# --- PATCH /change-password ---

async def test_change_password_204(logged_in_client):
    response = await logged_in_client.patch(
        _CHANGE_PASS,
        json={"old_password": "OldPass12", "new_password": "NewPass123"},
    )
    assert response.status_code == 204


async def test_change_password_400_weak_new(logged_in_client):
    response = await logged_in_client.patch(
        _CHANGE_PASS,
        json={"old_password": "OldPass12", "new_password": "short"},
    )
    assert response.status_code == 400


async def test_change_password_400_same_password(logged_in_client):
    response = await logged_in_client.patch(
        _CHANGE_PASS,
        json={"old_password": "SamePass12", "new_password": "SamePass12"},
    )
    assert response.status_code == 400


async def test_change_password_401_wrong_old(logged_in_client, mock_hasher):
    mock_hasher.verify.return_value = False
    response = await logged_in_client.patch(
        _CHANGE_PASS,
        json={"old_password": "WrongPass1", "new_password": "NewPass123"},
    )
    assert response.status_code == 401


async def test_change_password_401_no_token(public_client):
    response = await public_client.patch(
        _CHANGE_PASS,
        json={"old_password": "OldPass12", "new_password": "NewPass123"},
    )
    assert response.status_code == 401
