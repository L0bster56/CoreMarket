import uuid

from src.backend.application.comment.dtos.list_comments import ListCommentsCommand
from src.backend.application.comment.use_cases.list_comments import ListCommentsUseCase


class TestListCommentsUseCase:

    async def test_returns_top_level_comments(self, mock_uow, mock_comment_repo, item_id, sample_comment):
        mock_comment_repo.get_by_item.return_value = [sample_comment]
        use_case = ListCommentsUseCase(uow=mock_uow)

        result = await use_case.execute(ListCommentsCommand(item_id=item_id))

        assert len(result.items) == 1
        assert result.items[0].id == sample_comment.id

    async def test_returns_empty_when_no_comments(self, mock_uow, mock_comment_repo, item_id):
        mock_comment_repo.get_by_item.return_value = []
        use_case = ListCommentsUseCase(uow=mock_uow)

        result = await use_case.execute(ListCommentsCommand(item_id=item_id))

        assert result.items == []

    async def test_child_comment_nested_under_parent(
        self, mock_uow, mock_comment_repo, item_id, sample_comment, child_comment
    ):
        mock_comment_repo.get_by_item.return_value = [sample_comment, child_comment]
        use_case = ListCommentsUseCase(uow=mock_uow)

        result = await use_case.execute(ListCommentsCommand(item_id=item_id))

        assert len(result.items) == 1
        parent_node = result.items[0]
        assert len(parent_node.children) == 1
        assert parent_node.children[0].id == child_comment.id

    async def test_orphan_parent_id_goes_to_root(self, mock_uow, mock_comment_repo, item_id, user_id):
        from src.backend.domain.comment.entity import Comment
        comment_with_missing_parent = Comment.create(
            item_id=item_id,
            user_id=user_id,
            parent_id=uuid.uuid4(),
            body="Ответ на несуществующий",
        )
        mock_comment_repo.get_by_item.return_value = [comment_with_missing_parent]
        use_case = ListCommentsUseCase(uow=mock_uow)

        result = await use_case.execute(ListCommentsCommand(item_id=item_id))

        assert len(result.items) == 1

    async def test_get_by_item_called_with_correct_id(self, mock_uow, mock_comment_repo, item_id):
        mock_comment_repo.get_by_item.return_value = []
        use_case = ListCommentsUseCase(uow=mock_uow)

        await use_case.execute(ListCommentsCommand(item_id=item_id))

        mock_comment_repo.get_by_item.assert_called_once_with(item_id)
