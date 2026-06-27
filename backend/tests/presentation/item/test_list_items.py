from __future__ import annotations

from uuid import uuid4

from src.backend.application.item.dtos.list_items import ListItemsResult

ENDPOINT = "/api/v1/items"


async def test_list_items_200(anon_client, mock_list_uc):
    response = await anon_client.get(ENDPOINT)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    item = data["items"][0]
    assert item["title"] == "Test Item"
    assert "id" in item
    assert "category_id" in item
    assert "is_published" in item


async def test_list_items_200_empty(anon_client, mock_list_uc):
    mock_list_uc.execute.return_value = ListItemsResult(items=[], total=0)
    response = await anon_client.get(ENDPOINT)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


async def test_list_items_200_with_search(anon_client, mock_list_uc):
    response = await anon_client.get(ENDPOINT, params={"search": "laptop"})
    assert response.status_code == 200
    mock_list_uc.execute.assert_called_once()
    cmd = mock_list_uc.execute.call_args[0][0]
    assert cmd.filters.search == "laptop"


async def test_list_items_200_with_category_id(anon_client, mock_list_uc):
    cat_id = uuid4()
    response = await anon_client.get(ENDPOINT, params={"category_id": str(cat_id)})
    assert response.status_code == 200
    cmd = mock_list_uc.execute.call_args[0][0]
    assert cmd.filters.category_id == cat_id


async def test_list_items_200_with_tag(anon_client, mock_list_uc):
    response = await anon_client.get(ENDPOINT, params={"tag": "gaming"})
    assert response.status_code == 200
    cmd = mock_list_uc.execute.call_args[0][0]
    assert cmd.filters.tag == "gaming"


async def test_list_items_200_with_min_rating(anon_client, mock_list_uc):
    response = await anon_client.get(ENDPOINT, params={"min_rating": "4.0"})
    assert response.status_code == 200
    cmd = mock_list_uc.execute.call_args[0][0]
    assert cmd.filters.min_rating == 4.0


async def test_list_items_200_with_is_published(anon_client, mock_list_uc):
    response = await anon_client.get(ENDPOINT, params={"is_published": "true"})
    assert response.status_code == 200
    cmd = mock_list_uc.execute.call_args[0][0]
    assert cmd.filters.is_published is True


async def test_list_items_200_with_pagination(anon_client, mock_list_uc):
    response = await anon_client.get(ENDPOINT, params={"limit": "5", "offset": "10"})
    assert response.status_code == 200
    cmd = mock_list_uc.execute.call_args[0][0]
    assert cmd.filters.limit == 5
    assert cmd.filters.offset == 10
