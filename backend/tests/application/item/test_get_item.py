import pytest

from src.backend.application.item.dtos.get_item import GetItemCommand
from src.backend.application.item.errors import ItemNotFoundError
from src.backend.application.item.use_cases.get_item import GetItemUseCase


class TestGetItemUseCase:

    async def test_returns_item_with_all_fields(self, mock_uow, sample_item):
        mock_uow.items.get_by_id.return_value = sample_item
        mock_uow.characteristics.list_by_item.return_value = []
        mock_uow.gallery.list_by_item.return_value = []
        mock_uow.items.get_tags.return_value = []
        uc = GetItemUseCase(uow=mock_uow)

        result = await uc.execute(GetItemCommand(item_id=sample_item.id))

        assert result.id == sample_item.id
        assert result.title == str(sample_item.name)
        assert result.characteristics == []
        assert result.gallery == []
        assert result.tags == []

    async def test_raises_when_item_not_found(self, mock_uow, item_id):
        mock_uow.items.get_by_id.return_value = None
        uc = GetItemUseCase(uow=mock_uow)

        with pytest.raises(ItemNotFoundError):
            await uc.execute(GetItemCommand(item_id=item_id))

    async def test_includes_characteristics(self, mock_uow, sample_item, sample_characteristic):
        mock_uow.items.get_by_id.return_value = sample_item
        mock_uow.characteristics.list_by_item.return_value = [sample_characteristic]
        mock_uow.gallery.list_by_item.return_value = []
        mock_uow.items.get_tags.return_value = []
        uc = GetItemUseCase(uow=mock_uow)

        result = await uc.execute(GetItemCommand(item_id=sample_item.id))

        assert len(result.characteristics) == 1
        assert result.characteristics[0].id == sample_characteristic.id

    async def test_includes_gallery(self, mock_uow, sample_item, sample_gallery):
        mock_uow.items.get_by_id.return_value = sample_item
        mock_uow.characteristics.list_by_item.return_value = []
        mock_uow.gallery.list_by_item.return_value = [sample_gallery]
        mock_uow.items.get_tags.return_value = []
        uc = GetItemUseCase(uow=mock_uow)

        result = await uc.execute(GetItemCommand(item_id=sample_item.id))

        assert len(result.gallery) == 1
        assert result.gallery[0].image_url == sample_gallery.image_url

    async def test_includes_tags(self, mock_uow, sample_item, sample_tag):
        mock_uow.items.get_by_id.return_value = sample_item
        mock_uow.characteristics.list_by_item.return_value = []
        mock_uow.gallery.list_by_item.return_value = []
        mock_uow.items.get_tags.return_value = [sample_tag]
        uc = GetItemUseCase(uow=mock_uow)

        result = await uc.execute(GetItemCommand(item_id=sample_item.id))

        assert len(result.tags) == 1
        assert result.tags[0].slug == str(sample_tag.slug)

    async def test_commit_not_called(self, mock_uow, sample_item):
        mock_uow.items.get_by_id.return_value = sample_item
        mock_uow.characteristics.list_by_item.return_value = []
        mock_uow.gallery.list_by_item.return_value = []
        mock_uow.items.get_tags.return_value = []
        uc = GetItemUseCase(uow=mock_uow)

        await uc.execute(GetItemCommand(item_id=sample_item.id))

        mock_uow.commit.assert_called_once()
