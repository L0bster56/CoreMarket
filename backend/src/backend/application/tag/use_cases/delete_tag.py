from dataclasses import dataclass

from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.application.tag.dtos.delete_tag import DeleteTagCommand
from src.backend.application.tag.errors import TagNotFoundError


@dataclass
class DeleteTagUseCase:
    """
    UseCase: удаление тега по ID.

    Ответственность:
        - Проверка существования тега
        - Удаление тега из репозитория
    """

    uow: UnitOfWork

    async def execute(self, cmd: DeleteTagCommand) -> None:
        """
        Args:
            cmd (DeleteTagCommand): ID тега для удаления

        Raises:
            TagNotFoundError: если тег не найден
        """
        async with self.uow:
            tag = await self.uow.tags.get_by_id(cmd.tag_id)

            if tag is None:
                raise TagNotFoundError("tag not found")

            await self.uow.tags.delete(tag)
            await self.uow.commit()
