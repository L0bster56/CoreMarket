import uuid

import pytest

from src.backend.application.comment.dtos.delete_comment import DeleteCommentCommand
from src.backend.application.comment.errors import CommentNotFoundError, CommentEditForbiddenError
from src.backend.application.comment.use_cases.delete_comment import DeleteCommentUseCase


class TestDeleteCommentUseCase:

    async def test_owner_can_delete(self, mock_uow, mock_comment_repo, sample_comment, sample_user):
        mock_comment_repo.get_by_id.return_value = sample_comment
        use_case = DeleteCommentUseCase(uow=mock_uow, user=sample_user)
        cmd = DeleteCommentCommand(comment_id=sample_comment.id)

        await use_case.execute(cmd)

        mock_comment_repo.soft_delete.assert_called_once()

    async def test_admin_can_delete_any(self, mock_uow, mock_comment_repo, sample_comment, admin_user):
        mock_comment_repo.get_by_id.return_value = sample_comment
        use_case = DeleteCommentUseCase(uow=mock_uow, user=admin_user)
        cmd = DeleteCommentCommand(comment_id=sample_comment.id)

        await use_case.execute(cmd)

        mock_comment_repo.soft_delete.assert_called_once()

    async def test_raises_not_found_when_missing(self, mock_uow, mock_comment_repo, sample_user):
        mock_comment_repo.get_by_id.return_value = None
        use_case = DeleteCommentUseCase(uow=mock_uow, user=sample_user)
        cmd = DeleteCommentCommand(comment_id=uuid.uuid4())

        with pytest.raises(CommentNotFoundError):
            await use_case.execute(cmd)

    async def test_raises_forbidden_when_not_owner_and_not_admin(
        self, mock_uow, mock_comment_repo, sample_comment, other_user
    ):
        mock_comment_repo.get_by_id.return_value = sample_comment
        use_case = DeleteCommentUseCase(uow=mock_uow, user=other_user)
        cmd = DeleteCommentCommand(comment_id=sample_comment.id)

        with pytest.raises(CommentEditForbiddenError):
            await use_case.execute(cmd)

    async def test_commit_called_on_success(self, mock_uow, mock_comment_repo, sample_comment, sample_user):
        mock_comment_repo.get_by_id.return_value = sample_comment
        use_case = DeleteCommentUseCase(uow=mock_uow, user=sample_user)
        cmd = DeleteCommentCommand(comment_id=sample_comment.id)

        await use_case.execute(cmd)

        mock_uow.commit.assert_called_once()

    async def test_soft_delete_not_called_when_not_found(self, mock_uow, mock_comment_repo, sample_user):
        mock_comment_repo.get_by_id.return_value = None
        use_case = DeleteCommentUseCase(uow=mock_uow, user=sample_user)
        cmd = DeleteCommentCommand(comment_id=uuid.uuid4())

        with pytest.raises(CommentNotFoundError):
            await use_case.execute(cmd)

        mock_comment_repo.soft_delete.assert_not_called()
