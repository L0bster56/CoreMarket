import uuid

import pytest

from src.backend.application.comment.dtos.create_comment import CreateCommentCommand
from src.backend.application.comment.errors import CommentNotFoundError
from src.backend.application.comment.use_cases.create_comment import CreateCommentUseCase
from src.backend.domain.comment.entity import Comment


class TestCreateCommentUseCase:

    async def test_creates_top_level_comment(self, mock_uow, mock_comment_repo, item_id, sample_user, sample_comment):
        mock_comment_repo.create.return_value = sample_comment
        use_case = CreateCommentUseCase(uow=mock_uow, user=sample_user)
        cmd = CreateCommentCommand(item_id=item_id, body="Отличный товар!")

        result = await use_case.execute(cmd)

        assert result.id == sample_comment.id
        assert result.parent_id is None

    async def test_creates_reply_when_parent_exists(
        self, mock_uow, mock_comment_repo, item_id, sample_user, sample_comment, child_comment
    ):
        mock_comment_repo.get_by_id.return_value = sample_comment
        mock_comment_repo.create.return_value = child_comment
        use_case = CreateCommentUseCase(uow=mock_uow, user=sample_user)
        cmd = CreateCommentCommand(item_id=item_id, body="Согласен!", parent_id=sample_comment.id)

        result = await use_case.execute(cmd)

        assert result.parent_id == sample_comment.id

    async def test_raises_not_found_when_parent_missing(self, mock_uow, mock_comment_repo, item_id, sample_user):
        mock_comment_repo.get_by_id.return_value = None
        use_case = CreateCommentUseCase(uow=mock_uow, user=sample_user)
        cmd = CreateCommentCommand(item_id=item_id, body="Ответ", parent_id=uuid.uuid4())

        with pytest.raises(CommentNotFoundError):
            await use_case.execute(cmd)

    async def test_commit_called_on_success(self, mock_uow, mock_comment_repo, item_id, sample_user, sample_comment):
        mock_comment_repo.create.return_value = sample_comment
        use_case = CreateCommentUseCase(uow=mock_uow, user=sample_user)
        cmd = CreateCommentCommand(item_id=item_id, body="Текст")

        await use_case.execute(cmd)

        mock_uow.commit.assert_called_once()

    async def test_commit_not_called_when_parent_missing(self, mock_uow, mock_comment_repo, item_id, sample_user):
        mock_comment_repo.get_by_id.return_value = None
        use_case = CreateCommentUseCase(uow=mock_uow, user=sample_user)
        cmd = CreateCommentCommand(item_id=item_id, body="Текст", parent_id=uuid.uuid4())

        with pytest.raises(CommentNotFoundError):
            await use_case.execute(cmd)

        mock_uow.commit.assert_not_called()

    async def test_create_called_with_comment_entity(self, mock_uow, mock_comment_repo, item_id, sample_user, sample_comment):
        mock_comment_repo.create.return_value = sample_comment
        use_case = CreateCommentUseCase(uow=mock_uow, user=sample_user)
        cmd = CreateCommentCommand(item_id=item_id, body="Текст")

        await use_case.execute(cmd)

        created_arg = mock_comment_repo.create.call_args[0][0]
        assert isinstance(created_arg, Comment)
        assert created_arg.body == "Текст"
        assert created_arg.user_id == sample_user.id
