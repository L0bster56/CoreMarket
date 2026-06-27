from uuid import uuid4

import pytest

from src.backend.application.blog.dtos.add_blog_post_tag import RemoveBlogPostTagCommand
from src.backend.application.blog.errors import BlogPostNotFoundError
from src.backend.application.blog.use_cases.remove_blog_post_tag import RemoveBlogPostTagUseCase


class TestRemoveBlogPostTagUseCase:
    async def test_removes_tag_from_post(
        self, mock_uow, mock_blog_post_repo, sample_blog_post
    ):
        tag_id = uuid4()
        mock_blog_post_repo.get_by_slug.return_value = sample_blog_post
        uc = RemoveBlogPostTagUseCase(uow=mock_uow)

        await uc.execute(RemoveBlogPostTagCommand(slug="sample-post", tag_id=tag_id))

        mock_blog_post_repo.remove_tag.assert_called_once_with(sample_blog_post.id, tag_id)
        mock_uow.commit.assert_called_once()

    async def test_raises_not_found_for_missing_post(self, mock_uow, mock_blog_post_repo):
        mock_blog_post_repo.get_by_slug.return_value = None
        uc = RemoveBlogPostTagUseCase(uow=mock_uow)

        with pytest.raises(BlogPostNotFoundError):
            await uc.execute(RemoveBlogPostTagCommand(slug="missing", tag_id=uuid4()))
