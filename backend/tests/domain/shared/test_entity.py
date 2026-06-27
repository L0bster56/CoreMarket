import uuid
from dataclasses import dataclass

import pytest

from src.backend.domain.shared.entity import BaseEntity


# eq=False prevents @dataclass from overriding BaseEntity.__eq__ and __hash__
@dataclass(eq=False)
class StubEntity(BaseEntity):
    pass


class TestBaseEntityHash:
    def test_hash_equals_hash_of_id(self):
        e = StubEntity()
        assert hash(e) == hash(e.id)

    def test_two_entities_same_id_same_hash(self):
        uid = uuid.uuid4()
        e1 = StubEntity(id=uid)
        e2 = StubEntity(id=uid)
        assert hash(e1) == hash(e2)

    def test_two_entities_different_id_different_hash(self):
        e1 = StubEntity()
        e2 = StubEntity()
        assert hash(e1) != hash(e2)

    def test_entity_usable_as_dict_key(self):
        e = StubEntity()
        d = {e: "value"}
        assert d[e] == "value"

    def test_entity_usable_in_set(self):
        uid = uuid.uuid4()
        e1 = StubEntity(id=uid)
        e2 = StubEntity(id=uid)
        e3 = StubEntity()
        s = {e1, e2, e3}
        assert len(s) == 2


class TestBaseEntityEquality:
    def test_same_id_are_equal(self):
        uid = uuid.uuid4()
        e1 = StubEntity(id=uid)
        e2 = StubEntity(id=uid)
        assert e1 == e2

    def test_different_id_are_not_equal(self):
        e1 = StubEntity()
        e2 = StubEntity()
        assert e1 != e2

    def test_same_instance_is_equal_to_itself(self):
        e = StubEntity()
        assert e == e


class TestBaseEntityID:
    def test_default_id_is_uuid(self):
        e = StubEntity()
        assert isinstance(e.id, uuid.UUID)

    def test_each_instance_gets_unique_id(self):
        ids = {StubEntity().id for _ in range(10)}
        assert len(ids) == 10

    def test_custom_id_assigned(self):
        custom = uuid.uuid4()
        e = StubEntity(id=custom)
        assert e.id == custom
