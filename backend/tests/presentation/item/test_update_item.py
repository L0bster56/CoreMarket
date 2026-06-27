from __future__ import annotations

from uuid import uuid4

from src.backend.application.shared.errors import NotFoundError, BadRequestError

ENDPOINT = "/api/v1/items"


async def test_update_item_204(admin_client, mock_update_uc):
    response = await admin_client.patch(f"{ENDPOINT}/{uuid4()}", json={"title": "Updated"})
    assert response.status_code == 204


async def test_update_item_204_no_fields(admin_client, mock_update_uc):
    response = await admin_client.patch(f"{ENDPOINT}/{uuid4()}", json={})
    assert response.status_code == 204


async def test_update_item_204_publish(admin_client, mock_update_uc):
    response = await admin_client.patch(f"{ENDPOINT}/{uuid4()}", json={"is_published": True})
    assert response.status_code == 204


async def test_update_item_204_with_marketplace_links(admin_client, mock_update_uc):
    body = {
        "marketplace_links": [
            {"name": "Amazon", "url": "https://amazon.com/dp/B001", "price": "29.99"}
        ]
    }
    response = await admin_client.patch(f"{ENDPOINT}/{uuid4()}", json=body)
    assert response.status_code == 204


async def test_update_item_204_with_view_count(admin_client, mock_update_uc):
    response = await admin_client.patch(f"{ENDPOINT}/{uuid4()}", json={"view_count": 250})
    assert response.status_code == 204


async def test_update_item_422_view_count_zero(admin_client, mock_update_uc):
    response = await admin_client.patch(f"{ENDPOINT}/{uuid4()}", json={"view_count": 0})
    assert response.status_code == 422


async def test_update_item_422_view_count_negative(admin_client, mock_update_uc):
    response = await admin_client.patch(f"{ENDPOINT}/{uuid4()}", json={"view_count": -1})
    assert response.status_code == 422


async def test_update_item_400_invalid_view_count_from_domain(admin_client, mock_update_uc):
    mock_update_uc.execute.side_effect = BadRequestError("view_count must be >= 1, got 0")
    response = await admin_client.patch(f"{ENDPOINT}/{uuid4()}", json={"view_count": 1})
    assert response.status_code == 400


async def test_update_item_404(admin_client, mock_update_uc):
    mock_update_uc.execute.side_effect = NotFoundError("item not found")
    response = await admin_client.patch(f"{ENDPOINT}/{uuid4()}", json={"title": "X"})
    assert response.status_code == 404


async def test_update_item_403_regular_user(user_client, mock_update_uc):
    response = await user_client.patch(f"{ENDPOINT}/{uuid4()}", json={"title": "X"})
    assert response.status_code == 403


async def test_update_item_401_anon(anon_client, mock_update_uc):
    response = await anon_client.patch(f"{ENDPOINT}/{uuid4()}", json={"title": "X"})
    assert response.status_code == 401


async def test_update_item_422_invalid_uuid(admin_client, mock_update_uc):
    response = await admin_client.patch(f"{ENDPOINT}/not-a-uuid", json={"title": "X"})
    assert response.status_code == 422
