from __future__ import annotations

from src.backend.application.category.dtos.list_categories import ListCategoriesResult

ENDPOINT = "/api/v1/categories"


async def test_list_categories_200(anon_client, mock_list_uc):
    response = await anon_client.get(ENDPOINT)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["slug"] == "electronics"
    assert data[0]["name"] == "Electronics"


async def test_list_categories_returns_empty(anon_client, mock_list_uc):
    mock_list_uc.execute.return_value = ListCategoriesResult(items=[])
    response = await anon_client.get(ENDPOINT)
    assert response.status_code == 200
    assert response.json() == []
