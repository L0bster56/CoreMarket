from src.backend.application.item.dtos.list_items import ListItemsCommand, ListItemsFilters
from src.backend.application.item.use_cases.list_items import ListItemsUseCase


class TestListItemsUseCase:

    async def test_returns_items_and_total(self, mock_uow, sample_item):
        mock_uow.items.list.return_value = [sample_item]
        mock_uow.items.count.return_value = 1
        uc = ListItemsUseCase(uow=mock_uow)

        result = await uc.execute(ListItemsCommand())

        assert len(result.items) == 1
        assert result.total == 1

    async def test_returns_empty_list(self, mock_uow):
        mock_uow.items.list.return_value = []
        mock_uow.items.count.return_value = 0
        uc = ListItemsUseCase(uow=mock_uow)

        result = await uc.execute(ListItemsCommand())

        assert result.items == []
        assert result.total == 0

    async def test_item_entry_fields(self, mock_uow, sample_item):
        mock_uow.items.list.return_value = [sample_item]
        mock_uow.items.count.return_value = 1
        uc = ListItemsUseCase(uow=mock_uow)

        result = await uc.execute(ListItemsCommand())
        entry = result.items[0]

        assert entry.id == sample_item.id
        assert entry.title == str(sample_item.name)
        assert entry.short_description == sample_item.short_description
        assert entry.is_published == sample_item.is_published

    async def test_passes_filters_to_repo(self, mock_uow):
        mock_uow.items.list.return_value = []
        mock_uow.items.count.return_value = 0
        uc = ListItemsUseCase(uow=mock_uow)
        filters = ListItemsFilters(search="python", limit=5, offset=10)

        await uc.execute(ListItemsCommand(filters=filters))

        mock_uow.items.list.assert_called_once_with(filters)
        mock_uow.items.count.assert_called_once_with(filters)

    async def test_commit_not_called(self, mock_uow):
        mock_uow.items.list.return_value = []
        mock_uow.items.count.return_value = 0
        uc = ListItemsUseCase(uow=mock_uow)

        await uc.execute(ListItemsCommand())

        mock_uow.commit.assert_not_called()
