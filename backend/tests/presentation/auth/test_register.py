from __future__ import annotations

import pytest

ENDPOINT = "/api/v1/auth/register"
_VALID = {"username": "newuser", "email": "new@example.com", "password": "ValidPass1"}


async def test_register_201(public_client):
    response = await public_client.post(ENDPOINT, json=_VALID)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["username"] == "testuser"   # mock returns _sample_user
    assert data["email"] == "test@example.com"
    assert "password" not in data


async def test_register_409_email_exists(public_client, mock_uow):
    mock_uow.users.exists_email.return_value = True
    response = await public_client.post(ENDPOINT, json=_VALID)
    assert response.status_code == 409


async def test_register_409_username_exists(public_client, mock_uow):
    mock_uow.users.exists_username.return_value = True
    response = await public_client.post(ENDPOINT, json=_VALID)
    assert response.status_code == 409


async def test_register_400_weak_password(public_client):
    body = {"username": "user", "email": "u@example.com", "password": "short"}
    response = await public_client.post(ENDPOINT, json=body)
    assert response.status_code == 400


async def test_register_422_missing_email(public_client):
    response = await public_client.post(ENDPOINT, json={"username": "user", "password": "ValidPass1"})
    assert response.status_code == 422


async def test_register_422_missing_username(public_client):
    response = await public_client.post(ENDPOINT, json={"email": "u@example.com", "password": "ValidPass1"})
    assert response.status_code == 422
