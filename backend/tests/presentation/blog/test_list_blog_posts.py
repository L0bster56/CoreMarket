from __future__ import annotations

ENDPOINT = "/api/v1/blog/posts"


async def test_list_posts_200(anon_client, mock_list_posts_uc):
    response = await anon_client.get(ENDPOINT)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 1


async def test_list_posts_items_have_expected_fields(anon_client, mock_list_posts_uc):
    response = await anon_client.get(ENDPOINT)
    item = response.json()["items"][0]
    assert "id" in item
    assert "title" in item
    assert "slug" in item
    assert "status" in item
    assert "created_at" in item


async def test_list_posts_passes_status_filter(anon_client, mock_list_posts_uc):
    await anon_client.get(ENDPOINT, params={"post_status": "published"})
    cmd = mock_list_posts_uc.execute.call_args[0][0]
    assert cmd.filters.status == "published"


async def test_list_posts_passes_search_filter(anon_client, mock_list_posts_uc):
    await anon_client.get(ENDPOINT, params={"search": "python"})
    cmd = mock_list_posts_uc.execute.call_args[0][0]
    assert cmd.filters.search == "python"


async def test_list_posts_passes_tag_slug_filter(anon_client, mock_list_posts_uc):
    await anon_client.get(ENDPOINT, params={"tag_slug": "technology"})
    cmd = mock_list_posts_uc.execute.call_args[0][0]
    assert cmd.filters.tag_slug == "technology"


async def test_list_posts_passes_category_id_filter(anon_client, mock_list_posts_uc):
    from uuid import uuid4
    cat_id = str(uuid4())
    await anon_client.get(ENDPOINT, params={"category_id": cat_id})
    cmd = mock_list_posts_uc.execute.call_args[0][0]
    assert str(cmd.filters.category_id) == cat_id


async def test_list_posts_passes_pagination(anon_client, mock_list_posts_uc):
    await anon_client.get(ENDPOINT, params={"limit": 5, "offset": 10})
    cmd = mock_list_posts_uc.execute.call_args[0][0]
    assert cmd.filters.limit == 5
    assert cmd.filters.offset == 10


async def test_list_posts_accessible_without_auth(anon_client, mock_list_posts_uc):
    response = await anon_client.get(ENDPOINT)
    assert response.status_code == 200
