from dataclasses import dataclass

from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.application.tag.dtos.get_tag import GetTagCommand, GetTagResult
from src.backend.application.tag.errors import TagNotFoundError


@dataclass
class GetTagUseCase:
    """
    UseCase: получение тега по ID.

    Ответственность:
        - Проверка существования тега
        - Возврат данных тега
    """

    uow: UnitOfWork

    async def execute(self, cmd: GetTagCommand) -> GetTagResult:
        """
        Args:
            cmd (GetTagCommand): ID тега

        Returns:
            GetTagResult: данные тега

        Raises:
            TagNotFoundError: если тег не найден
        """
        async with self.uow:
            tag = await self.uow.tags.get_by_id(cmd.tag_id)

            if tag is None:
                raise TagNotFoundError("tag not found")

            return GetTagResult(id=tag.id, name=str(tag.name), slug=str(tag.slug))
