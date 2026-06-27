from __future__ import annotations

from uuid import uuid4

from src.backend.application.shared.errors import NotFoundError

ENDPOINT = "/api/v1/items"


async def test_get_item_200(anon_client, mock_get_uc):
    response = await anon_client.get(f"{ENDPOINT}/{uuid4()}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Item"
    assert data["short_description"] == "Short desc"
    assert data["description"] == "Full description"
    assert data["is_published"] is True
    assert "id" in data
    assert "category_id" in data
    assert "characteristics" in data
    assert "gallery" in data
    assert "tags" in data
    assert "marketplace_links" in data
    assert "created_at" in data
    assert "updated_at" in data


async def test_get_item_404(anon_client, mock_get_uc):
    mock_get_uc.execute.side_effect = NotFoundError("item not found")
    response = await anon_client.get(f"{ENDPOINT}/{uuid4()}")
    assert response.status_code == 404


async def test_get_item_422_invalid_uuid(anon_client, mock_get_uc):
    response = await anon_client.get(f"{ENDPOINT}/not-a-uuid")
    assert response.status_code == 422
