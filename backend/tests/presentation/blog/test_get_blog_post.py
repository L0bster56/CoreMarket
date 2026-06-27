from __future__ import annotations

from src.backend.application.blog.errors import BlogPostNotFoundError

SLUG = "test-post"
ENDPOINT = f"/api/v1/blog/posts/{SLUG}"


async def test_get_post_200(anon_client, mock_get_post_uc):
    response = await anon_client.get(ENDPOINT)
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == SLUG
    assert "title" in data
    assert "status" in data
    assert "tags" in data
    assert "product_links" in data
    assert "content_html" in data


async def test_get_post_404_when_not_found(anon_client, mock_get_post_uc):
    mock_get_post_uc.execute.side_effect = BlogPostNotFoundError("not found")
    response = await anon_client.get(ENDPOINT)
    assert response.status_code == 404


async def test_get_post_passes_slug_to_use_case(anon_client, mock_get_post_uc):
    await anon_client.get(ENDPOINT)
    cmd = mock_get_post_uc.execute.call_args[0][0]
    assert cmd.slug == SLUG


async def test_get_post_accessible_without_auth(anon_client, mock_get_post_uc):
    response = await anon_client.get(ENDPOINT)
    assert response.status_code == 200
