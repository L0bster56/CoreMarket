import pytest
from uuid import uuid4

from src.backend.application.item.dtos.add_characteristic import AddCharacteristicCommand
from src.backend.application.item.dtos.delete_characteristic import DeleteCharacteristicCommand
from src.backend.application.item.dtos.update_characteristic import UpdateCharacteristicCommand
from src.backend.application.item.errors import (
    CharacteristicNotFoundError,
    ItemEditForbiddenError,
    ItemNotFoundError,
)
from src.backend.application.item.use_cases.add_characteristic import AddCharacteristicUseCase
from src.backend.application.item.use_cases.delete_characteristic import DeleteCharacteristicUseCase
from src.backend.application.item.use_cases.update_characteristic import UpdateCharacteristicUseCase


class TestAddCharacteristicUseCase:

    async def test_admin_adds_characteristic(self, mock_uow, admin_user, sample_item, sample_characteristic):
        mock_uow.items.get_by_id.return_value = sample_item
        mock_uow.characteristics.create.return_value = sample_characteristic
        uc = AddCharacteristicUseCase(uow=mock_uow, user=admin_user)

        result = await uc.execute(AddCharacteristicCommand(
            item_id=sample_item.id, name="Weight", value="1kg"
        ))

        assert result.id == sample_characteristic.id
        mock_uow.commit.assert_called_once()

    async def test_non_admin_raises_forbidden(self, mock_uow, regular_user, item_id):
        uc = AddCharacteristicUseCase(uow=mock_uow, user=regular_user)

        with pytest.raises(ItemEditForbiddenError):
            await uc.execute(AddCharacteristicCommand(item_id=item_id, name="W", value="1kg"))

    async def test_raises_when_item_not_found(self, mock_uow, admin_user):
        mock_uow.items.get_by_id.return_value = None
        uc = AddCharacteristicUseCase(uow=mock_uow, user=admin_user)

        with pytest.raises(ItemNotFoundError):
            await uc.execute(AddCharacteristicCommand(item_id=uuid4(), name="W", value="1kg"))


class TestUpdateCharacteristicUseCase:

    async def test_admin_updates_characteristic(self, mock_uow, admin_user, sample_characteristic):
        mock_uow.characteristics.get_by_id.return_value = sample_characteristic
        uc = UpdateCharacteristicUseCase(uow=mock_uow, user=admin_user)

        result = await uc.execute(UpdateCharacteristicCommand(
            characteristic_id=sample_characteristic.id, name="Height", value="2m"
        ))

        assert result.id == sample_characteristic.id
        assert result.name == "Height"
        assert result.value == "2m"
        mock_uow.commit.assert_called_once()

    async def test_non_admin_raises_forbidden(self, mock_uow, regular_user):
        uc = UpdateCharacteristicUseCase(uow=mock_uow, user=regular_user)

        with pytest.raises(ItemEditForbiddenError):
            await uc.execute(UpdateCharacteristicCommand(characteristic_id=uuid4(), value="2m"))

    async def test_raises_when_not_found(self, mock_uow, admin_user):
        mock_uow.characteristics.get_by_id.return_value = None
        uc = UpdateCharacteristicUseCase(uow=mock_uow, user=admin_user)

        with pytest.raises(CharacteristicNotFoundError):
            await uc.execute(UpdateCharacteristicCommand(characteristic_id=uuid4()))

    async def test_skips_none_fields(self, mock_uow, admin_user, sample_characteristic):
        original_value = sample_characteristic.value
        mock_uow.characteristics.get_by_id.return_value = sample_characteristic
        uc = UpdateCharacteristicUseCase(uow=mock_uow, user=admin_user)

        await uc.execute(UpdateCharacteristicCommand(characteristic_id=sample_characteristic.id, name="NewName"))

        assert sample_characteristic.value == original_value


class TestDeleteCharacteristicUseCase:

    async def test_admin_deletes_characteristic(self, mock_uow, admin_user, sample_characteristic):
        mock_uow.characteristics.get_by_id.return_value = sample_characteristic
        uc = DeleteCharacteristicUseCase(uow=mock_uow, user=admin_user)

        await uc.execute(DeleteCharacteristicCommand(characteristic_id=sample_characteristic.id))

        mock_uow.characteristics.delete.assert_called_once_with(sample_characteristic)
        mock_uow.commit.assert_called_once()

    async def test_non_admin_raises_forbidden(self, mock_uow, regular_user):
        uc = DeleteCharacteristicUseCase(uow=mock_uow, user=regular_user)

        with pytest.raises(ItemEditForbiddenError):
            await uc.execute(DeleteCharacteristicCommand(characteristic_id=uuid4()))

    async def test_raises_when_not_found(self, mock_uow, admin_user):
        mock_uow.characteristics.get_by_id.return_value = None
        uc = DeleteCharacteristicUseCase(uow=mock_uow, user=admin_user)

        with pytest.raises(CharacteristicNotFoundError):
            await uc.execute(DeleteCharacteristicCommand(characteristic_id=uuid4()))
