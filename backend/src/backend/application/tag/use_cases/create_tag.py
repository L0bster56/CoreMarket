from dataclasses import dataclass

from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.application.tag.dtos.create_tag import CreateTagCommand, CreateTagResult
from src.backend.application.tag.errors import TagSlugAlreadyExistsError
from src.backend.domain.tag.entity import Tag


@dataclass
class CreateTagUseCase:
    """
    UseCase: создание нового тега.

    Ответственность:
        - Проверка уникальности slug
        - Создание и сохранение тега
    """

    uow: UnitOfWork

    async def execute(self, cmd: CreateTagCommand) -> CreateTagResult:
        """
        Args:
            cmd (CreateTagCommand): данные нового тега

        Returns:
            CreateTagResult: данные созданного тега

        Raises:
            TagSlugAlreadyExistsError: если slug уже занят
        """
        async with self.uow:
            if await self.uow.tags.exists_slug(cmd.slug):
                raise TagSlugAlreadyExistsError("slug already exists")

            tag = Tag.create(name=cmd.name, slug=cmd.slug)
            created = await self.uow.tags.create(tag)
            await self.uow.commit()

            return CreateTagResult(
                id=created.id,
                name=str(created.name),
                slug=str(created.slug),
            )
