from dataclasses import dataclass

from src.backend.application.item.dtos.add_characteristic import (
    AddCharacteristicCommand,
    AddCharacteristicResult,
)
from src.backend.application.item.errors import ItemNotFoundError, ItemEditForbiddenError
from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.domain.item.characteristic import Characteristic
from src.backend.domain.user.entity import User, UserRole


@dataclass
class AddCharacteristicUseCase:
    uow: UnitOfWork
    user: User

    async def execute(self, cmd: AddCharacteristicCommand) -> AddCharacteristicResult:
        if self.user.role != UserRole.admin:
            raise ItemEditForbiddenError("only admin can manage characteristics")

        async with self.uow:
            item = await self.uow.items.get_by_id(cmd.item_id)
            if item is None:
                raise ItemNotFoundError("item not found")

            characteristic = Characteristic.create(
                item_id=cmd.item_id,
                name=cmd.name,
                value=cmd.value,
                group=cmd.group,
            )
            created = await self.uow.characteristics.create(characteristic)
            await self.uow.commit()

            return AddCharacteristicResult(
                id=created.id,
                item_id=created.item_id,
                name=created.name,
                value=created.value,
                group=created.group,
            )
