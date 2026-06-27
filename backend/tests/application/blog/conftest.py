from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.backend.domain.blog.entity import BlogPost, BlogTag
from src.backend.domain.blog.enums import BlogPostStatus


@pytest.fixture
def mock_blog_post_repo():
    return AsyncMock()


@pytest.fixture
def mock_blog_tag_repo():
    return AsyncMock()


@pytest.fixture
def mock_category_repo():
    return AsyncMock()


@pytest.fixture
def mock_uow(mock_blog_post_repo, mock_blog_tag_repo, mock_category_repo):
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.commit = AsyncMock()
    uow.rollback = AsyncMock()
    uow.blog_posts = mock_blog_post_repo
    uow.blog_tags = mock_blog_tag_repo
    uow.categories = mock_category_repo
    return uow


@pytest.fixture
def sample_blog_post() -> BlogPost:
    return BlogPost.create(
        title="Sample Post",
        slug="sample-post",
        short_description="A sample post for testing",
    )


@pytest.fixture
def publishable_blog_post() -> BlogPost:
    post = BlogPost.create(title="Publishable Post", slug="publishable-post")
    post.set_category(uuid4())
    post.set_content("# Hello\n\nSome content here.")
    return post


@pytest.fixture
def published_blog_post(publishable_blog_post: BlogPost) -> BlogPost:
    publishable_blog_post.publish()
    return publishable_blog_post


@pytest.fixture
def sample_blog_tag() -> BlogTag:
    return BlogTag.create(name="Technology", slug="technology")


def make_blog_post_result(post: BlogPost) -> dict:
    return {
        "id": post.id,
        "title": post.title,
        "slug": str(post.slug),
        "short_description": post.short_description,
        "status": post.status.value,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
    }
