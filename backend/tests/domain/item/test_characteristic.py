import uuid

import pytest

from src.backend.domain.item.characteristic import Characteristic
from src.backend.domain.shared.value_objects.name.error import InvalidNameError
from src.backend.domain.shared.value_objects.name.value_object import Name


class TestCharacteristic:
    def test_create_characteristic(self):
        item_id = uuid.uuid4()
        ch = Characteristic(
            item_id=item_id,
            name=Name("Процессор"),
            value="Apple A17 Pro",
        )
        assert ch.item_id == item_id
        assert str(ch.name) == "Процессор"
        assert ch.value == "Apple A17 Pro"

    def test_id_is_uuid(self):
        ch = Characteristic(
            item_id=uuid.uuid4(),
            name=Name("RAM"),
            value="8 GB",
        )
        assert isinstance(ch.id, uuid.UUID)

    def test_unique_ids(self):
        item_id = uuid.uuid4()
        c1 = Characteristic(item_id=item_id, name=Name("RAM"), value="8 GB")
        c2 = Characteristic(item_id=item_id, name=Name("Storage"), value="256 GB")
        assert c1.id != c2.id

    def test_invalid_name_raises(self):
        with pytest.raises(InvalidNameError):
            Characteristic(item_id=uuid.uuid4(), name=Name("X"), value="val")

    def test_equality_by_id(self):
        uid = uuid.uuid4()
        item_id = uuid.uuid4()
        c1 = Characteristic(id=uid, item_id=item_id, name=Name("RAM"), value="8 GB")
        c2 = Characteristic(id=uid, item_id=item_id, name=Name("Storage"), value="256 GB")
        assert c1 == c2
