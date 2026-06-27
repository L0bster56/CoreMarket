from uuid import uuid4

import pytest

from src.backend.application.blog.dtos.link_product import (
    LinkProductCommand,
    UnlinkProductCommand,
)
from src.backend.application.blog.errors import BlogPostNotFoundError
from src.backend.application.blog.use_cases.link_product import LinkProductUseCase, UnlinkProductUseCase
from src.backend.domain.blog.product_link import BlogProductLink


class TestLinkProductUseCase:
    async def test_links_product_to_post(
        self, mock_uow, mock_blog_post_repo, sample_blog_post
    ):
        product_id = uuid4()
        link = BlogProductLink(
            blog_post_id=sample_blog_post.id,
            product_id=product_id,
            display_order=2,
        )
        mock_blog_post_repo.get_by_slug.return_value = sample_blog_post
        mock_blog_post_repo.add_product_link.return_value = link
        uc = LinkProductUseCase(uow=mock_uow)

        result = await uc.execute(
            LinkProductCommand(slug="sample-post", product_id=product_id, display_order=2)
        )

        assert result.product_id == product_id
        assert result.display_order == 2
        mock_uow.commit.assert_called_once()

    async def test_raises_not_found_for_missing_post(self, mock_uow, mock_blog_post_repo):
        mock_blog_post_repo.get_by_slug.return_value = None
        uc = LinkProductUseCase(uow=mock_uow)

        with pytest.raises(BlogPostNotFoundError):
            await uc.execute(
                LinkProductCommand(slug="missing", product_id=uuid4(), display_order=0)
            )

    async def test_default_display_order_is_zero(
        self, mock_uow, mock_blog_post_repo, sample_blog_post
    ):
        product_id = uuid4()
        link = BlogProductLink(
            blog_post_id=sample_blog_post.id,
            product_id=product_id,
        )
        mock_blog_post_repo.get_by_slug.return_value = sample_blog_post
        mock_blog_post_repo.add_product_link.return_value = link
        uc = LinkProductUseCase(uow=mock_uow)

        result = await uc.execute(
            LinkProductCommand(slug="sample-post", product_id=product_id)
        )

        assert result.display_order == 0


class TestUnlinkProductUseCase:
    async def test_unlinks_product_from_post(
        self, mock_uow, mock_blog_post_repo, sample_blog_post
    ):
        link_id = uuid4()
        mock_blog_post_repo.get_by_slug.return_value = sample_blog_post
        uc = UnlinkProductUseCase(uow=mock_uow)

        await uc.execute(UnlinkProductCommand(slug="sample-post", link_id=link_id))

        mock_blog_post_repo.remove_product_link.assert_called_once_with(link_id)
        mock_uow.commit.assert_called_once()

    async def test_raises_not_found_for_missing_post(self, mock_uow, mock_blog_post_repo):
        mock_blog_post_repo.get_by_slug.return_value = None
        uc = UnlinkProductUseCase(uow=mock_uow)

        with pytest.raises(BlogPostNotFoundError):
            await uc.execute(UnlinkProductCommand(slug="missing", link_id=uuid4()))
