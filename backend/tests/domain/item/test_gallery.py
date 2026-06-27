import uuid

import pytest

from src.backend.domain.item.gallery import Gallery


class TestGallery:
    def test_create_gallery(self):
        item_id = uuid.uuid4()
        g = Gallery(item_id=item_id, image_url="/media/items/photo.jpg")
        assert g.item_id == item_id
        assert g.image_url == "/media/items/photo.jpg"

    def test_id_is_uuid(self):
        g = Gallery(item_id=uuid.uuid4(), image_url="/media/items/img.jpg")
        assert isinstance(g.id, uuid.UUID)

    def test_unique_ids(self):
        item_id = uuid.uuid4()
        g1 = Gallery(item_id=item_id, image_url="/img1.jpg")
        g2 = Gallery(item_id=item_id, image_url="/img2.jpg")
        assert g1.id != g2.id

    def test_equality_by_id(self):
        uid = uuid.uuid4()
        item_id = uuid.uuid4()
        g1 = Gallery(id=uid, item_id=item_id, image_url="/img1.jpg")
        g2 = Gallery(id=uid, item_id=item_id, image_url="/img2.jpg")
        assert g1 == g2

    def test_different_ids_not_equal(self):
        item_id = uuid.uuid4()
        g1 = Gallery(item_id=item_id, image_url="/img1.jpg")
        g2 = Gallery(item_id=item_id, image_url="/img1.jpg")
        assert g1 != g2
