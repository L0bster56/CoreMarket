from dataclasses import dataclass

from src.backend.application.category.dtos.update_category import UpdateCategoryCommand
from src.backend.application.category.errors import CategoryNotFoundError
from src.backend.application.shared.interfaces.uow import UnitOfWork


@dataclass
class UpdateCategoryUseCase:
    """
    UseCase: обновление данных категории.

    Ответственность:
        - Проверка существования категории
        - Обновление name, description, image_url
        - Сохранение изменений
    """

    uow: UnitOfWork

    async def execute(self, cmd: UpdateCategoryCommand) -> None:
        """
        Обновляет категорию.

        Args:
            cmd (UpdateCategoryCommand): поля для обновления (все опциональны)

        Raises:
            CategoryNotFoundError: если категория не найдена
        """
        async with self.uow:
            category = await self.uow.categories.get_by_id(cmd.category_id)

            if category is None:
                raise CategoryNotFoundError("category not found")

            if cmd.name is not None:
                category.change_name(cmd.name)

            if cmd.description is not None:
                category.change_description(cmd.description)

            if cmd.image_url is not None:
                category.change_image_url(cmd.image_url)

            await self.uow.categories.update(category)
            await self.uow.commit()
