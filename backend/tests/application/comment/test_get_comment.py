import uuid

import pytest

from src.backend.application.comment.dtos.get_comment import GetCommentCommand
from src.backend.application.comment.errors import CommentNotFoundError
from src.backend.application.comment.use_cases.get_comment import GetCommentUseCase


class TestGetCommentUseCase:

    async def test_returns_comment_when_found(self, mock_uow, mock_comment_repo, sample_comment):
        mock_comment_repo.get_by_id.return_value = sample_comment
        use_case = GetCommentUseCase(uow=mock_uow)

        result = await use_case.execute(GetCommentCommand(comment_id=sample_comment.id))

        assert result.id == sample_comment.id
        assert result.body == sample_comment.body
        assert result.user_id == sample_comment.user_id

    async def test_raises_not_found_when_missing(self, mock_uow, mock_comment_repo):
        mock_comment_repo.get_by_id.return_value = None
        use_case = GetCommentUseCase(uow=mock_uow)

        with pytest.raises(CommentNotFoundError):
            await use_case.execute(GetCommentCommand(comment_id=uuid.uuid4()))

    async def test_get_by_id_called_with_correct_id(self, mock_uow, mock_comment_repo, sample_comment):
        mock_comment_repo.get_by_id.return_value = sample_comment
        use_case = GetCommentUseCase(uow=mock_uow)

        await use_case.execute(GetCommentCommand(comment_id=sample_comment.id))

        mock_comment_repo.get_by_id.assert_called_once_with(sample_comment.id)
