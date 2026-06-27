from __future__ import annotations

from uuid import uuid4

ENDPOINT = "/api/v1/items"

_VALID = {
    "title": "Test Item",
    "short_description": "Short desc",
    "description": "Full description",
    "category_id": str(uuid4()),
}


async def test_create_item_201(admin_client, mock_create_uc):
    response = await admin_client.post(ENDPOINT, json=_VALID)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Item"
    assert data["short_description"] == "Short desc"
    assert "id" in data
    assert "is_published" in data
    assert data["characteristics"] == []
    assert data["gallery"] == []
    assert data["tags"] == []


async def test_create_item_201_with_marketplace_links(admin_client, mock_create_uc):
    body = {
        **_VALID,
        "marketplace_links": [
            {"name": "DNS", "url": "https://dns.ru/product/123", "price": "9990"}
        ],
    }
    response = await admin_client.post(ENDPOINT, json=body)
    assert response.status_code == 201


async def test_create_item_201_with_youtube(admin_client, mock_create_uc):
    body = {**_VALID, "youtube_url": "https://youtube.com/watch?v=abc"}
    response = await admin_client.post(ENDPOINT, json=body)
    assert response.status_code == 201


async def test_create_item_403_regular_user(user_client, mock_create_uc):
    response = await user_client.post(ENDPOINT, json=_VALID)
    assert response.status_code == 403


async def test_create_item_401_anon(anon_client, mock_create_uc):
    response = await anon_client.post(ENDPOINT, json=_VALID)
    assert response.status_code == 401


async def test_create_item_422_missing_title(admin_client, mock_create_uc):
    body = {k: v for k, v in _VALID.items() if k != "title"}
    response = await admin_client.post(ENDPOINT, json=body)
    assert response.status_code == 422


async def test_create_item_422_missing_description(admin_client, mock_create_uc):
    body = {k: v for k, v in _VALID.items() if k != "description"}
    response = await admin_client.post(ENDPOINT, json=body)
    assert response.status_code == 422


async def test_create_item_422_missing_category_id(admin_client, mock_create_uc):
    body = {k: v for k, v in _VALID.items() if k != "category_id"}
    response = await admin_client.post(ENDPOINT, json=body)
    assert response.status_code == 422
