import pytest
from uuid import uuid4

from src.backend.application.item.dtos.add_item_tag import AddItemTagCommand
from src.backend.application.item.dtos.remove_item_tag import RemoveItemTagCommand
from src.backend.application.item.errors import (
    ItemEditForbiddenError,
    ItemNotFoundError,
    ItemTagAlreadyAttachedError,
    ItemTagNotFoundError,
)
from src.backend.application.item.use_cases.add_item_tag import AddItemTagUseCase
from src.backend.application.item.use_cases.remove_item_tag import RemoveItemTagUseCase


class TestAddItemTagUseCase:

    async def test_admin_adds_tag_successfully(self, mock_uow, admin_user, sample_item, sample_tag):
        mock_uow.items.get_by_id.return_value = sample_item
        mock_uow.tags.get_by_id.return_value = sample_tag
        mock_uow.items.get_tags.return_value = []
        uc = AddItemTagUseCase(uow=mock_uow, user=admin_user)

        await uc.execute(AddItemTagCommand(item_id=sample_item.id, tag_id=sample_tag.id))

        mock_uow.items.add_tag.assert_called_once_with(sample_item.id, sample_tag.id)
        mock_uow.commit.assert_called_once()

    async def test_non_admin_raises_forbidden(self, mock_uow, regular_user, item_id):
        uc = AddItemTagUseCase(uow=mock_uow, user=regular_user)

        with pytest.raises(ItemEditForbiddenError):
            await uc.execute(AddItemTagCommand(item_id=item_id, tag_id=uuid4()))

    async def test_raises_when_item_not_found(self, mock_uow, admin_user, sample_tag):
        mock_uow.items.get_by_id.return_value = None
        uc = AddItemTagUseCase(uow=mock_uow, user=admin_user)

        with pytest.raises(ItemNotFoundError):
            await uc.execute(AddItemTagCommand(item_id=uuid4(), tag_id=sample_tag.id))

    async def test_raises_when_tag_not_found(self, mock_uow, admin_user, sample_item):
        mock_uow.items.get_by_id.return_value = sample_item
        mock_uow.tags.get_by_id.return_value = None
        uc = AddItemTagUseCase(uow=mock_uow, user=admin_user)

        with pytest.raises(ItemTagNotFoundError):
            await uc.execute(AddItemTagCommand(item_id=sample_item.id, tag_id=uuid4()))

    async def test_raises_when_tag_already_attached(self, mock_uow, admin_user, sample_item, sample_tag):
        mock_uow.items.get_by_id.return_value = sample_item
        mock_uow.tags.get_by_id.return_value = sample_tag
        mock_uow.items.get_tags.return_value = [sample_tag]
        uc = AddItemTagUseCase(uow=mock_uow, user=admin_user)

        with pytest.raises(ItemTagAlreadyAttachedError):
            await uc.execute(AddItemTagCommand(item_id=sample_item.id, tag_id=sample_tag.id))


class TestRemoveItemTagUseCase:

    async def test_admin_removes_tag_successfully(self, mock_uow, admin_user, sample_item, sample_tag):
        mock_uow.items.get_by_id.return_value = sample_item
        mock_uow.items.get_tags.return_value = [sample_tag]
        uc = RemoveItemTagUseCase(uow=mock_uow, user=admin_user)

        await uc.execute(RemoveItemTagCommand(item_id=sample_item.id, tag_id=sample_tag.id))

        mock_uow.items.remove_tag.assert_called_once_with(sample_item.id, sample_tag.id)
        mock_uow.commit.assert_called_once()

    async def test_non_admin_raises_forbidden(self, mock_uow, regular_user, item_id):
        uc = RemoveItemTagUseCase(uow=mock_uow, user=regular_user)

        with pytest.raises(ItemEditForbiddenError):
            await uc.execute(RemoveItemTagCommand(item_id=item_id, tag_id=uuid4()))

    async def test_raises_when_item_not_found(self, mock_uow, admin_user):
        mock_uow.items.get_by_id.return_value = None
        uc = RemoveItemTagUseCase(uow=mock_uow, user=admin_user)

        with pytest.raises(ItemNotFoundError):
            await uc.execute(RemoveItemTagCommand(item_id=uuid4(), tag_id=uuid4()))

    async def test_raises_when_tag_not_attached(self, mock_uow, admin_user, sample_item, sample_tag):
        mock_uow.items.get_by_id.return_value = sample_item
        mock_uow.items.get_tags.return_value = []
        uc = RemoveItemTagUseCase(uow=mock_uow, user=admin_user)

        with pytest.raises(ItemTagNotFoundError):
            await uc.execute(RemoveItemTagCommand(item_id=sample_item.id, tag_id=sample_tag.id))
