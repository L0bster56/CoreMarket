from dataclasses import dataclass

from src.backend.application.category.dtos.create_category import CreateCategoryCommand, CreateCategoryResult
from src.backend.application.category.errors import CategorySlugAlreadyExistsError
from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.domain.category.entity import Category


@dataclass
class CreateCategoryUseCase:
    """
    UseCase: создание новой категории.

    Ответственность:
        - Проверка уникальности slug
        - Создание и сохранение категории
    """

    uow: UnitOfWork

    async def execute(self, cmd: CreateCategoryCommand) -> CreateCategoryResult:
        """
        Создаёт новую категорию.

        Args:
            cmd (CreateCategoryCommand): данные новой категории

        Returns:
            CreateCategoryResult: данные созданной категории

        Raises:
            CategorySlugAlreadyExistsError: если slug уже занят
        """
        async with self.uow:
            if await self.uow.categories.exists_slug(cmd.slug):
                raise CategorySlugAlreadyExistsError("slug already exists")

            category = Category.create(
                name=cmd.name,
                slug=cmd.slug,
                description=cmd.description,
                image_url=cmd.image_url,
            )

            created = await self.uow.categories.create(category)
            await self.uow.commit()

            return CreateCategoryResult(
                id=created.id,
                name=str(created.name),
                slug=str(created.slug),
                description=created.description,
                image_url=created.image_url,
                created_at=created.created_at,
                updated_at=created.updated_at,
            )
