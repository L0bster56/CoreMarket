from dataclasses import dataclass

from src.backend.application.category.dtos.get_category import GetCategoryCommand, GetCategoryResult
from src.backend.application.category.errors import CategoryNotFoundError
from src.backend.application.shared.interfaces.uow import UnitOfWork


@dataclass
class GetCategoryUseCase:
    """
    UseCase: получение категории по идентификатору.

    Ответственность:
        - Поиск категории по ID
        - Возврат данных категории
    """

    uow: UnitOfWork

    async def execute(self, cmd: GetCategoryCommand) -> GetCategoryResult:
        """
        Возвращает категорию по ID.

        Args:
            cmd (GetCategoryCommand): идентификатор категории

        Returns:
            GetCategoryResult: данные категории

        Raises:
            CategoryNotFoundError: если категория не найдена
        """
        async with self.uow:
            category = await self.uow.categories.get_by_id(cmd.category_id)

            if category is None:
                raise CategoryNotFoundError("category not found")

            return GetCategoryResult(
                id=category.id,
                name=str(category.name),
                slug=str(category.slug),
                description=category.description,
                image_url=category.image_url,
                created_at=category.created_at,
                updated_at=category.updated_at,
            )
