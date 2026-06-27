from __future__ import annotations

from uuid import uuid4

from src.backend.application.shared.errors import NotFoundError

ENDPOINT = "/api/v1/items"

_VALID_CHAR = {"name": "Color", "value": "Red"}


async def test_add_characteristic_201(admin_client, mock_add_char_uc):
    response = await admin_client.post(f"{ENDPOINT}/{uuid4()}/characteristics", json=_VALID_CHAR)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Color"
    assert data["value"] == "Red"
    assert "id" in data


async def test_add_characteristic_404(admin_client, mock_add_char_uc):
    mock_add_char_uc.execute.side_effect = NotFoundError("item not found")
    response = await admin_client.post(f"{ENDPOINT}/{uuid4()}/characteristics", json=_VALID_CHAR)
    assert response.status_code == 404


async def test_add_characteristic_403_regular_user(user_client, mock_add_char_uc):
    response = await user_client.post(f"{ENDPOINT}/{uuid4()}/characteristics", json=_VALID_CHAR)
    assert response.status_code == 403


async def test_add_characteristic_401_anon(anon_client, mock_add_char_uc):
    response = await anon_client.post(f"{ENDPOINT}/{uuid4()}/characteristics", json=_VALID_CHAR)
    assert response.status_code == 401


async def test_add_characteristic_422_missing_name(admin_client, mock_add_char_uc):
    response = await admin_client.post(f"{ENDPOINT}/{uuid4()}/characteristics", json={"value": "Red"})
    assert response.status_code == 422


async def test_add_characteristic_422_missing_value(admin_client, mock_add_char_uc):
    response = await admin_client.post(f"{ENDPOINT}/{uuid4()}/characteristics", json={"name": "Color"})
    assert response.status_code == 422


async def test_update_characteristic_204(admin_client, mock_update_char_uc):
    response = await admin_client.patch(
        f"{ENDPOINT}/{uuid4()}/characteristics/{uuid4()}",
        json={"name": "Size", "value": "XL"},
    )
    assert response.status_code == 204


async def test_update_characteristic_204_no_fields(admin_client, mock_update_char_uc):
    response = await admin_client.patch(
        f"{ENDPOINT}/{uuid4()}/characteristics/{uuid4()}",
        json={},
    )
    assert response.status_code == 204


async def test_update_characteristic_404(admin_client, mock_update_char_uc):
    mock_update_char_uc.execute.side_effect = NotFoundError("characteristic not found")
    response = await admin_client.patch(
        f"{ENDPOINT}/{uuid4()}/characteristics/{uuid4()}",
        json={"name": "X"},
    )
    assert response.status_code == 404


async def test_update_characteristic_403_regular_user(user_client, mock_update_char_uc):
    response = await user_client.patch(
        f"{ENDPOINT}/{uuid4()}/characteristics/{uuid4()}",
        json={"name": "X"},
    )
    assert response.status_code == 403


async def test_update_characteristic_401_anon(anon_client, mock_update_char_uc):
    response = await anon_client.patch(
        f"{ENDPOINT}/{uuid4()}/characteristics/{uuid4()}",
        json={"name": "X"},
    )
    assert response.status_code == 401


async def test_delete_characteristic_204(admin_client, mock_delete_char_uc):
    response = await admin_client.delete(f"{ENDPOINT}/{uuid4()}/characteristics/{uuid4()}")
    assert response.status_code == 204


async def test_delete_characteristic_404(admin_client, mock_delete_char_uc):
    mock_delete_char_uc.execute.side_effect = NotFoundError("characteristic not found")
    response = await admin_client.delete(f"{ENDPOINT}/{uuid4()}/characteristics/{uuid4()}")
    assert response.status_code == 404


async def test_delete_characteristic_403_regular_user(user_client, mock_delete_char_uc):
    response = await user_client.delete(f"{ENDPOINT}/{uuid4()}/characteristics/{uuid4()}")
    assert response.status_code == 403


async def test_delete_characteristic_401_anon(anon_client, mock_delete_char_uc):
    response = await anon_client.delete(f"{ENDPOINT}/{uuid4()}/characteristics/{uuid4()}")
    assert response.status_code == 401
