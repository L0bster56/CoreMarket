from __future__ import annotations

from uuid import uuid4

from fastapi import HTTPException

from src.backend.main import app
from src.backend.presentation.api.v1.category.dependencies import get_current_category

ENDPOINT = "/api/v1/categories"


async def test_get_category_200(anon_client, mock_current_category):
    response = await anon_client.get(f"{ENDPOINT}/{uuid4()}")
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "electronics"
    assert data["name"] == "Electronics"
    assert data["description"] == "All gadgets"
    assert "id" in data
    assert "created_at" in data


async def test_get_category_404(anon_client):
    def _not_found():
        raise HTTPException(status_code=404, detail="Category not found")

    app.dependency_overrides[get_current_category] = _not_found
    try:
        response = await anon_client.get(f"{ENDPOINT}/{uuid4()}")
        assert response.status_code == 404
    finally:
        app.dependency_overrides.pop(get_current_category, None)


async def test_get_category_invalid_uuid(anon_client):
    response = await anon_client.get(f"{ENDPOINT}/not-a-uuid")
    assert response.status_code == 422
