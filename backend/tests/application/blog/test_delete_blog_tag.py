from uuid import uuid4

import pytest

from src.backend.application.blog.dtos.blog_tags import DeleteBlogTagCommand
from src.backend.application.blog.errors import BlogTagNotFoundError
from src.backend.application.blog.use_cases.delete_blog_tag import DeleteBlogTagUseCase


class TestDeleteBlogTagUseCase:
    async def test_deletes_existing_tag(self, mock_uow, mock_blog_tag_repo, sample_blog_tag):
        mock_blog_tag_repo.get_by_id.return_value = sample_blog_tag
        uc = DeleteBlogTagUseCase(uow=mock_uow)

        await uc.execute(DeleteBlogTagCommand(tag_id=sample_blog_tag.id))

        mock_blog_tag_repo.delete.assert_called_once_with(sample_blog_tag)
        mock_uow.commit.assert_called_once()

    async def test_raises_not_found_for_missing_tag(self, mock_uow, mock_blog_tag_repo):
        mock_blog_tag_repo.get_by_id.return_value = None
        uc = DeleteBlogTagUseCase(uow=mock_uow)

        with pytest.raises(BlogTagNotFoundError):
            await uc.execute(DeleteBlogTagCommand(tag_id=uuid4()))
