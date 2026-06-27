from dataclasses import dataclass

from src.backend.application.item.dtos.add_gallery_image import (
    AddGalleryImageCommand,
    AddGalleryImageResult,
)
from src.backend.application.item.errors import ItemNotFoundError, ItemEditForbiddenError
from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.domain.item.gallery import Gallery
from src.backend.domain.user.entity import User, UserRole


@dataclass
class AddGalleryImageUseCase:
    uow: UnitOfWork
    user: User

    async def execute(self, cmd: AddGalleryImageCommand) -> AddGalleryImageResult:
        if self.user.role != UserRole.admin:
            raise ItemEditForbiddenError("only admin can manage gallery")

        async with self.uow:
            item = await self.uow.items.get_by_id(cmd.item_id)
            if item is None:
                raise ItemNotFoundError("item not found")

            gallery_image = Gallery.create(item_id=cmd.item_id, image_url=cmd.image_url)
            created = await self.uow.gallery.create(gallery_image)
            await self.uow.commit()

            return AddGalleryImageResult(
                id=created.id,
                item_id=created.item_id,
                image_url=created.image_url,
            )
