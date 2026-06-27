from __future__ import annotations

from src.backend.application.blog.errors import BlogPostNotFoundError
from src.backend.application.shared.errors import BadRequestError

SLUG = "test-post"


async def test_publish_204_admin(admin_client, mock_publish_uc):
    response = await admin_client.post(f"/api/v1/blog/posts/{SLUG}/publish")
    assert response.status_code == 204


async def test_publish_403_regular_user(user_client, mock_publish_uc):
    response = await user_client.post(f"/api/v1/blog/posts/{SLUG}/publish")
    assert response.status_code == 403


async def test_publish_401_anon(anon_client, mock_publish_uc):
    response = await anon_client.post(f"/api/v1/blog/posts/{SLUG}/publish")
    assert response.status_code == 401


async def test_publish_404_not_found(admin_client, mock_publish_uc):
    mock_publish_uc.execute.side_effect = BlogPostNotFoundError("not found")
    response = await admin_client.post(f"/api/v1/blog/posts/{SLUG}/publish")
    assert response.status_code == 404


async def test_publish_400_bad_request(admin_client, mock_publish_uc):
    mock_publish_uc.execute.side_effect = BadRequestError("Post must have content before publishing")
    response = await admin_client.post(f"/api/v1/blog/posts/{SLUG}/publish")
    assert response.status_code == 400


async def test_unpublish_204_admin(admin_client, mock_unpublish_uc):
    response = await admin_client.post(f"/api/v1/blog/posts/{SLUG}/unpublish")
    assert response.status_code == 204


async def test_unpublish_403_regular_user(user_client, mock_unpublish_uc):
    response = await user_client.post(f"/api/v1/blog/posts/{SLUG}/unpublish")
    assert response.status_code == 403


async def test_unpublish_401_anon(anon_client, mock_unpublish_uc):
    response = await anon_client.post(f"/api/v1/blog/posts/{SLUG}/unpublish")
    assert response.status_code == 401


async def test_unpublish_404_not_found(admin_client, mock_unpublish_uc):
    mock_unpublish_uc.execute.side_effect = BlogPostNotFoundError("not found")
    response = await admin_client.post(f"/api/v1/blog/posts/{SLUG}/unpublish")
    assert response.status_code == 404


async def test_archive_204_admin(admin_client, mock_archive_uc):
    response = await admin_client.post(f"/api/v1/blog/posts/{SLUG}/archive")
    assert response.status_code == 204


async def test_archive_403_regular_user(user_client, mock_archive_uc):
    response = await user_client.post(f"/api/v1/blog/posts/{SLUG}/archive")
    assert response.status_code == 403


async def test_archive_401_anon(anon_client, mock_archive_uc):
    response = await anon_client.post(f"/api/v1/blog/posts/{SLUG}/archive")
    assert response.status_code == 401


async def test_archive_404_not_found(admin_client, mock_archive_uc):
    mock_archive_uc.execute.side_effect = BlogPostNotFoundError("not found")
    response = await admin_client.post(f"/api/v1/blog/posts/{SLUG}/archive")
    assert response.status_code == 404
