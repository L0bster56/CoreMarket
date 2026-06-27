import uuid

import pytest

from src.backend.application.comment.dtos.update_comment import UpdateCommentCommand
from src.backend.application.comment.errors import CommentNotFoundError, CommentEditForbiddenError
from src.backend.application.comment.use_cases.update_comment import UpdateCommentUseCase


class TestUpdateCommentUseCase:

    async def test_updates_body_successfully(self, mock_uow, mock_comment_repo, sample_comment, sample_user):
        mock_comment_repo.get_by_id.return_value = sample_comment
        use_case = UpdateCommentUseCase(uow=mock_uow, user=sample_user)
        cmd = UpdateCommentCommand(comment_id=sample_comment.id, body="Изменённый текст")

        await use_case.execute(cmd)

        mock_comment_repo.update.assert_called_once()

    async def test_raises_not_found_when_missing(self, mock_uow, mock_comment_repo, sample_user):
        mock_comment_repo.get_by_id.return_value = None
        use_case = UpdateCommentUseCase(uow=mock_uow, user=sample_user)
        cmd = UpdateCommentCommand(comment_id=uuid.uuid4(), body="Текст")

        with pytest.raises(CommentNotFoundError):
            await use_case.execute(cmd)

    async def test_raises_forbidden_when_not_owner(self, mock_uow, mock_comment_repo, sample_comment, other_user):
        mock_comment_repo.get_by_id.return_value = sample_comment
        use_case = UpdateCommentUseCase(uow=mock_uow, user=other_user)
        cmd = UpdateCommentCommand(comment_id=sample_comment.id, body="Текст")

        with pytest.raises(CommentEditForbiddenError):
            await use_case.execute(cmd)

    async def test_commit_called_on_success(self, mock_uow, mock_comment_repo, sample_comment, sample_user):
        mock_comment_repo.get_by_id.return_value = sample_comment
        use_case = UpdateCommentUseCase(uow=mock_uow, user=sample_user)
        cmd = UpdateCommentCommand(comment_id=sample_comment.id, body="Новый текст")

        await use_case.execute(cmd)

        mock_uow.commit.assert_called_once()

    async def test_commit_not_called_when_forbidden(self, mock_uow, mock_comment_repo, sample_comment, other_user):
        mock_comment_repo.get_by_id.return_value = sample_comment
        use_case = UpdateCommentUseCase(uow=mock_uow, user=other_user)
        cmd = UpdateCommentCommand(comment_id=sample_comment.id, body="Текст")

        with pytest.raises(CommentEditForbiddenError):
            await use_case.execute(cmd)

        mock_uow.commit.assert_not_called()
