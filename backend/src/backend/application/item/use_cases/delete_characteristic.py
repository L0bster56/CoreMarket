from dataclasses import dataclass

from src.backend.application.item.dtos.delete_characteristic import DeleteCharacteristicCommand
from src.backend.application.item.errors import CharacteristicNotFoundError, ItemEditForbiddenError
from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.domain.user.entity import User, UserRole


@dataclass
class DeleteCharacteristicUseCase:
    uow: UnitOfWork
    user: User

    async def execute(self, cmd: DeleteCharacteristicCommand) -> None:
        if self.user.role != UserRole.admin:
            raise ItemEditForbiddenError("only admin can manage characteristics")

        async with self.uow:
            characteristic = await self.uow.characteristics.get_by_id(cmd.characteristic_id)
            if characteristic is None:
                raise CharacteristicNotFoundError("characteristic not found")

            await self.uow.characteristics.delete(characteristic)
            await self.uow.commit()
