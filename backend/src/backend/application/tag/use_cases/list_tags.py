from dataclasses import dataclass

from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.application.tag.dtos.list_tags import ListTagsCommand, ListTagsResult, TagSummary


@dataclass
class ListTagsUseCase:
    """
    UseCase: получение списка всех тегов.

    Ответственность:
        - Загрузка всех тегов из репозитория
        - Преобразование в DTO
    """

    uow: UnitOfWork

    async def execute(self, cmd: ListTagsCommand) -> ListTagsResult:
        """
        Args:
            cmd (ListTagsCommand): пустая команда

        Returns:
            ListTagsResult: список тегов
        """
        async with self.uow:
            all_tags = await self.uow.tags.list_all()
            return ListTagsResult(
                items=[
                    TagSummary(id=tag.id, name=str(tag.name), slug=str(tag.slug))
                    for tag in all_tags
                ]
            )
