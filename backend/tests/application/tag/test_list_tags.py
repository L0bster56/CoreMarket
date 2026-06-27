from src.backend.application.tag.dtos.list_tags import ListTagsCommand
from src.backend.application.tag.use_cases.list_tags import ListTagsUseCase


class TestListTagsUseCase:

    async def test_returns_all_tags(self, mock_uow, mock_tag_repo, sample_tag, another_tag):
        mock_tag_repo.list_all.return_value = [sample_tag, another_tag]
        use_case = ListTagsUseCase(uow=mock_uow)

        result = await use_case.execute(ListTagsCommand())

        assert len(result.items) == 2

    async def test_returns_empty_when_no_tags(self, mock_uow, mock_tag_repo):
        mock_tag_repo.list_all.return_value = []
        use_case = ListTagsUseCase(uow=mock_uow)

        result = await use_case.execute(ListTagsCommand())

        assert result.items == []

    async def test_result_contains_correct_fields(self, mock_uow, mock_tag_repo, sample_tag):
        mock_tag_repo.list_all.return_value = [sample_tag]
        use_case = ListTagsUseCase(uow=mock_uow)

        result = await use_case.execute(ListTagsCommand())

        item = result.items[0]
        assert item.id == sample_tag.id
        assert item.name == str(sample_tag.name)
        assert item.slug == str(sample_tag.slug)

    async def test_list_all_called_once(self, mock_uow, mock_tag_repo):
        mock_tag_repo.list_all.return_value = []
        use_case = ListTagsUseCase(uow=mock_uow)

        await use_case.execute(ListTagsCommand())

        mock_tag_repo.list_all.assert_called_once()
