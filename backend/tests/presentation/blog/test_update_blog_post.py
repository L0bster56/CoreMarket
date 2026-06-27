from __future__ import annotations

from src.backend.application.blog.errors import BlogPostNotFoundError
from src.backend.application.shared.errors import ConflictError

SLUG = "test-post"
ENDPOINT = f"/api/v1/blog/posts/{SLUG}"


async def test_update_post_204_admin(admin_client, mock_update_post_uc):
    response = await admin_client.patch(ENDPOINT, json={"title": "New Title"})
    assert response.status_code == 204


async def test_update_post_403_regular_user(user_client, mock_update_post_uc):
    response = await user_client.patch(ENDPOINT, json={"title": "New Title"})
    assert response.status_code == 403


async def test_update_post_401_anon(anon_client, mock_update_post_uc):
    response = await anon_client.patch(ENDPOINT, json={"title": "New Title"})
    assert response.status_code == 401


async def test_update_post_404_not_found(admin_client, mock_update_post_uc):
    mock_update_post_uc.execute.side_effect = BlogPostNotFoundError("not found")
    response = await admin_client.patch(ENDPOINT, json={"title": "New Title"})
    assert response.status_code == 404


async def test_update_post_409_slug_conflict(admin_client, mock_update_post_uc):
    mock_update_post_uc.execute.side_effect = ConflictError("slug exists")
    response = await admin_client.patch(ENDPOINT, json={"new_slug": "taken-slug"})
    assert response.status_code == 409


async def test_update_post_empty_body_is_valid(admin_client, mock_update_post_uc):
    response = await admin_client.patch(ENDPOINT, json={})
    assert response.status_code == 204


async def test_update_post_passes_slug_from_path(admin_client, mock_update_post_uc):
    await admin_client.patch(ENDPOINT, json={"title": "New Title"})
    cmd = mock_update_post_uc.execute.call_args[0][0]
    assert cmd.slug == SLUG
