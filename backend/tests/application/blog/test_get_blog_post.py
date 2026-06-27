from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from src.backend.application.blog.dtos.get_blog_post import (
    BlogCategoryResult,
    GetBlogPostCommand,
)
from src.backend.application.blog.errors import BlogPostNotFoundError
from src.backend.application.blog.use_cases.get_blog_post import GetBlogPostUseCase
from src.backend.domain.blog.entity import BlogTag
from src.backend.domain.blog.product_link import BlogProductLink


class TestGetBlogPostUseCase:
    def _make_uc(self, mock_uow, rendered_html: str = "<p>Content</p>"):
        renderer = MagicMock()
        renderer.render.return_value = rendered_html
        return GetBlogPostUseCase(uow=mock_uow, renderer=renderer)

    async def test_returns_result_for_existing_post(
        self, mock_uow, mock_blog_post_repo, sample_blog_post
    ):
        sample_blog_post.set_content("# Hello")
        mock_blog_post_repo.get_by_slug.return_value = sample_blog_post
        mock_blog_post_repo.get_tags.return_value = []
        mock_blog_post_repo.get_product_links.return_value = []
        uc = self._make_uc(mock_uow)

        result = await uc.execute(GetBlogPostCommand(slug="sample-post"))

        assert result.id == sample_blog_post.id
        assert result.title == "Sample Post"
        assert result.slug == "sample-post"
        assert result.content == "# Hello"
        assert result.content_html == "<p>Content</p>"

    async def test_raises_not_found_for_missing_post(self, mock_uow, mock_blog_post_repo):
        mock_blog_post_repo.get_by_slug.return_value = None
        uc = self._make_uc(mock_uow)

        with pytest.raises(BlogPostNotFoundError):
            await uc.execute(GetBlogPostCommand(slug="missing"))

    async def test_includes_tags_in_result(
        self, mock_uow, mock_blog_post_repo, sample_blog_post
    ):
        sample_blog_post.set_content("Content")
        tag = BlogTag.create(name="Python", slug="python")
        mock_blog_post_repo.get_by_slug.return_value = sample_blog_post
        mock_blog_post_repo.get_tags.return_value = [tag]
        mock_blog_post_repo.get_product_links.return_value = []
        uc = self._make_uc(mock_uow)

        result = await uc.execute(GetBlogPostCommand(slug="sample-post"))

        assert len(result.tags) == 1
        assert result.tags[0].slug == "python"

    async def test_includes_product_links_in_result(
        self, mock_uow, mock_blog_post_repo, sample_blog_post
    ):
        sample_blog_post.set_content("Content")
        link = BlogProductLink(
            blog_post_id=sample_blog_post.id,
            product_id=uuid4(),
            display_order=1,
        )
        mock_blog_post_repo.get_by_slug.return_value = sample_blog_post
        mock_blog_post_repo.get_tags.return_value = []
        mock_blog_post_repo.get_product_links.return_value = [link]
        uc = self._make_uc(mock_uow)

        result = await uc.execute(GetBlogPostCommand(slug="sample-post"))

        assert len(result.product_links) == 1
        assert result.product_links[0].display_order == 1

    async def test_includes_category_when_present(
        self, mock_uow, mock_blog_post_repo, mock_category_repo, sample_blog_post
    ):
        from src.backend.domain.category.entity import Category
        cat_id = uuid4()
        sample_blog_post.set_category(cat_id)
        sample_blog_post.set_content("Content")
        category = Category.create(name="Technology", slug="technology")
        category.id = cat_id

        mock_blog_post_repo.get_by_slug.return_value = sample_blog_post
        mock_blog_post_repo.get_tags.return_value = []
        mock_blog_post_repo.get_product_links.return_value = []
        mock_category_repo.get_by_id.return_value = category
        uc = self._make_uc(mock_uow)

        result = await uc.execute(GetBlogPostCommand(slug="sample-post"))

        assert result.category is not None
        assert result.category.slug == "technology"

    async def test_content_html_none_when_content_is_none(
        self, mock_uow, mock_blog_post_repo, sample_blog_post
    ):
        sample_blog_post.content = None
        mock_blog_post_repo.get_by_slug.return_value = sample_blog_post
        mock_blog_post_repo.get_tags.return_value = []
        mock_blog_post_repo.get_product_links.return_value = []
        renderer = MagicMock()
        uc = GetBlogPostUseCase(uow=mock_uow, renderer=renderer)

        result = await uc.execute(GetBlogPostCommand(slug="sample-post"))

        assert result.content_html is None
        renderer.render.assert_not_called()

    async def test_category_is_none_when_no_category_id(
        self, mock_uow, mock_blog_post_repo, sample_blog_post
    ):
        sample_blog_post.set_content("Content")
        sample_blog_post.category_id = None
        mock_blog_post_repo.get_by_slug.return_value = sample_blog_post
        mock_blog_post_repo.get_tags.return_value = []
        mock_blog_post_repo.get_product_links.return_value = []
        uc = self._make_uc(mock_uow)

        result = await uc.execute(GetBlogPostCommand(slug="sample-post"))

        assert result.category is None
