from dataclasses import dataclass

from src.backend.application.item.dtos.update_characteristic import (
    UpdateCharacteristicCommand,
    UpdateCharacteristicResult,
)
from src.backend.application.item.errors import CharacteristicNotFoundError, ItemEditForbiddenError
from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.domain.user.entity import User, UserRole


@dataclass
class UpdateCharacteristicUseCase:
    uow: UnitOfWork
    user: User

    async def execute(self, cmd: UpdateCharacteristicCommand) -> UpdateCharacteristicResult:
        if self.user.role != UserRole.admin:
            raise ItemEditForbiddenError("only admin can manage characteristics")

        async with self.uow:
            characteristic = await self.uow.characteristics.get_by_id(cmd.characteristic_id)
            if characteristic is None:
                raise CharacteristicNotFoundError("characteristic not found")

            if cmd.name is not None:
                characteristic.name = cmd.name

            if cmd.value is not None:
                characteristic.value = cmd.value

            if cmd.group is not None:
                characteristic.group = cmd.group

            await self.uow.characteristics.update(characteristic)
            await self.uow.commit()

            return UpdateCharacteristicResult(
                id=characteristic.id,
                item_id=characteristic.item_id,
                name=characteristic.name,
                value=characteristic.value,
                group=characteristic.group,
            )
