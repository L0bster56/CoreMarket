from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from unittest.mock import AsyncMock

from src.backend.application.blog.dtos.blog_tags import BlogTagItem, ListBlogTagsResult
from src.backend.application.blog.dtos.create_blog_post import CreateBlogPostResult
from src.backend.application.blog.dtos.get_blog_post import (
    GetBlogPostResult,
    BlogTagResult,
    BlogProductLinkResult,
)
from src.backend.application.blog.dtos.list_blog_posts import (
    BlogPostListEntry,
    ListBlogPostsResult,
)
from src.backend.application.blog.dtos.link_product import LinkProductResult
from src.backend.main import app
from src.backend.presentation.api.v1.blog.dependencies import (
    get_add_blog_post_tag_uc,
    get_archive_blog_post_uc,
    get_create_blog_post_uc,
    get_create_blog_tag_uc,
    get_delete_blog_post_uc,
    get_delete_blog_tag_uc,
    get_get_blog_post_uc,
    get_link_product_uc,
    get_list_blog_posts_uc,
    get_list_blog_tags_uc,
    get_publish_blog_post_uc,
    get_remove_blog_post_tag_uc,
    get_unlink_product_uc,
    get_unpublish_blog_post_uc,
    get_update_blog_post_uc,
    get_update_blog_tag_uc,
)

_NOW = datetime.now(tz=timezone.utc)
_POST_ID = uuid4()
_POST_SLUG = "test-post"


def _make_list_posts_result(count: int = 1) -> ListBlogPostsResult:
    items = [
        BlogPostListEntry(
            id=uuid4(),
            title=f"Post {i}",
            slug=f"post-{i}",
            short_description=f"Desc {i}",
            cover_image_url=None,
            category_id=None,
            status="draft",
            created_at=_NOW,
            updated_at=_NOW,
        )
        for i in range(count)
    ]
    return ListBlogPostsResult(items=items, total=count)


def _make_get_post_result(slug: str = _POST_SLUG) -> GetBlogPostResult:
    return GetBlogPostResult(
        id=_POST_ID,
        title="Test Post",
        slug=slug,
        short_description="A test post",
        content="# Hello",
        content_html="<h1>Hello</h1>",
        cover_image_url=None,
        category_id=None,
        category=None,
        status="draft",
        seo_title=None,
        seo_description=None,
        tags=[],
        product_links=[],
        created_at=_NOW,
        updated_at=_NOW,
    )


def _make_create_post_result() -> CreateBlogPostResult:
    return CreateBlogPostResult(
        id=_POST_ID,
        title="New Post",
        slug="new-post",
        short_description=None,
        status="draft",
        created_at=_NOW,
        updated_at=_NOW,
    )


def _make_link_result() -> LinkProductResult:
    return LinkProductResult(id=uuid4(), product_id=uuid4(), display_order=0)


def _make_list_tags_result() -> ListBlogTagsResult:
    return ListBlogTagsResult(
        items=[
            BlogTagItem(id=uuid4(), name="Python", slug="python"),
            BlogTagItem(id=uuid4(), name="Django", slug="django"),
        ]
    )


@pytest.fixture
def mock_list_posts_uc():
    uc = AsyncMock()
    uc.execute.return_value = _make_list_posts_result()
    app.dependency_overrides[get_list_blog_posts_uc] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_list_blog_posts_uc, None)


@pytest.fixture
def mock_get_post_uc():
    uc = AsyncMock()
    uc.execute.return_value = _make_get_post_result()
    app.dependency_overrides[get_get_blog_post_uc] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_get_blog_post_uc, None)


@pytest.fixture
def mock_create_post_uc():
    uc = AsyncMock()
    uc.execute.return_value = _make_create_post_result()
    app.dependency_overrides[get_create_blog_post_uc] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_create_blog_post_uc, None)


@pytest.fixture
def mock_update_post_uc():
    uc = AsyncMock()
    uc.execute.return_value = None
    app.dependency_overrides[get_update_blog_post_uc] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_update_blog_post_uc, None)


@pytest.fixture
def mock_delete_post_uc():
    uc = AsyncMock()
    uc.execute.return_value = None
    app.dependency_overrides[get_delete_blog_post_uc] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_delete_blog_post_uc, None)


@pytest.fixture
def mock_publish_uc():
    uc = AsyncMock()
    uc.execute.return_value = None
    app.dependency_overrides[get_publish_blog_post_uc] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_publish_blog_post_uc, None)


@pytest.fixture
def mock_unpublish_uc():
    uc = AsyncMock()
    uc.execute.return_value = None
    app.dependency_overrides[get_unpublish_blog_post_uc] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_unpublish_blog_post_uc, None)


@pytest.fixture
def mock_archive_uc():
    uc = AsyncMock()
    uc.execute.return_value = None
    app.dependency_overrides[get_archive_blog_post_uc] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_archive_blog_post_uc, None)


@pytest.fixture
def mock_add_tag_uc():
    uc = AsyncMock()
    uc.execute.return_value = None
    app.dependency_overrides[get_add_blog_post_tag_uc] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_add_blog_post_tag_uc, None)


@pytest.fixture
def mock_remove_tag_uc():
    uc = AsyncMock()
    uc.execute.return_value = None
    app.dependency_overrides[get_remove_blog_post_tag_uc] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_remove_blog_post_tag_uc, None)


@pytest.fixture
def mock_link_product_uc():
    uc = AsyncMock()
    uc.execute.return_value = _make_link_result()
    app.dependency_overrides[get_link_product_uc] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_link_product_uc, None)


@pytest.fixture
def mock_unlink_product_uc():
    uc = AsyncMock()
    uc.execute.return_value = None
    app.dependency_overrides[get_unlink_product_uc] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_unlink_product_uc, None)


@pytest.fixture
def mock_list_tags_uc():
    uc = AsyncMock()
    uc.execute.return_value = _make_list_tags_result()
    app.dependency_overrides[get_list_blog_tags_uc] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_list_blog_tags_uc, None)


@pytest.fixture
def mock_create_tag_uc():
    from src.backend.application.blog.dtos.blog_tags import CreateBlogTagResult
    uc = AsyncMock()
    uc.execute.return_value = CreateBlogTagResult(id=uuid4(), name="Python", slug="python")
    app.dependency_overrides[get_create_blog_tag_uc] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_create_blog_tag_uc, None)


@pytest.fixture
def mock_update_tag_uc():
    uc = AsyncMock()
    uc.execute.return_value = None
    app.dependency_overrides[get_update_blog_tag_uc] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_update_blog_tag_uc, None)


@pytest.fixture
def mock_delete_tag_uc():
    uc = AsyncMock()
    uc.execute.return_value = None
    app.dependency_overrides[get_delete_blog_tag_uc] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_delete_blog_tag_uc, None)
