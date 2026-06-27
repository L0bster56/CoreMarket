import pytest
from uuid import uuid4

from src.backend.application.item.dtos.add_gallery_image import AddGalleryImageCommand
from src.backend.application.item.dtos.delete_gallery_image import DeleteGalleryImageCommand
from src.backend.application.item.errors import (
    GalleryImageNotFoundError,
    ItemEditForbiddenError,
    ItemNotFoundError,
)
from src.backend.application.item.use_cases.add_gallery_image import AddGalleryImageUseCase
from src.backend.application.item.use_cases.delete_gallery_image import DeleteGalleryImageUseCase


class TestAddGalleryImageUseCase:

    async def test_admin_adds_image(self, mock_uow, admin_user, sample_item, sample_gallery):
        mock_uow.items.get_by_id.return_value = sample_item
        mock_uow.gallery.create.return_value = sample_gallery
        uc = AddGalleryImageUseCase(uow=mock_uow, user=admin_user)

        result = await uc.execute(AddGalleryImageCommand(
            item_id=sample_item.id, image_url="/media/items/new.jpg"
        ))

        assert result.id == sample_gallery.id
        assert result.image_url == sample_gallery.image_url
        mock_uow.commit.assert_called_once()

    async def test_non_admin_raises_forbidden(self, mock_uow, regular_user, item_id):
        uc = AddGalleryImageUseCase(uow=mock_uow, user=regular_user)

        with pytest.raises(ItemEditForbiddenError):
            await uc.execute(AddGalleryImageCommand(item_id=item_id, image_url="/media/img.jpg"))

    async def test_raises_when_item_not_found(self, mock_uow, admin_user):
        mock_uow.items.get_by_id.return_value = None
        uc = AddGalleryImageUseCase(uow=mock_uow, user=admin_user)

        with pytest.raises(ItemNotFoundError):
            await uc.execute(AddGalleryImageCommand(item_id=uuid4(), image_url="/media/img.jpg"))

    async def test_commit_not_called_on_forbidden(self, mock_uow, regular_user, item_id):
        uc = AddGalleryImageUseCase(uow=mock_uow, user=regular_user)

        with pytest.raises(ItemEditForbiddenError):
            await uc.execute(AddGalleryImageCommand(item_id=item_id, image_url="/media/img.jpg"))

        mock_uow.commit.assert_not_called()


class TestDeleteGalleryImageUseCase:

    async def test_admin_deletes_image(self, mock_uow, admin_user, sample_gallery):
        mock_uow.gallery.get_by_id.return_value = sample_gallery
        uc = DeleteGalleryImageUseCase(uow=mock_uow, user=admin_user)

        await uc.execute(DeleteGalleryImageCommand(gallery_id=sample_gallery.id))

        mock_uow.gallery.delete.assert_called_once_with(sample_gallery)
        mock_uow.commit.assert_called_once()

    async def test_non_admin_raises_forbidden(self, mock_uow, regular_user):
        uc = DeleteGalleryImageUseCase(uow=mock_uow, user=regular_user)

        with pytest.raises(ItemEditForbiddenError):
            await uc.execute(DeleteGalleryImageCommand(gallery_id=uuid4()))

    async def test_raises_when_image_not_found(self, mock_uow, admin_user):
        mock_uow.gallery.get_by_id.return_value = None
        uc = DeleteGalleryImageUseCase(uow=mock_uow, user=admin_user)

        with pytest.raises(GalleryImageNotFoundError):
            await uc.execute(DeleteGalleryImageCommand(gallery_id=uuid4()))
