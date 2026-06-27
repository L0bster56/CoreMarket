import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

import pytest

from src.backend.domain.shared.mixins import IDMixin, TimeActionMixin


@dataclass(kw_only=True)
class StubID(IDMixin):
    pass


@dataclass(kw_only=True)
class StubTimestamp(TimeActionMixin):
    pass


class TestIDMixin:
    def test_default_id_is_uuid(self):
        obj = StubID()
        assert isinstance(obj.id, uuid.UUID)

    def test_unique_ids_per_instance(self):
        ids = {StubID().id for _ in range(20)}
        assert len(ids) == 20

    def test_custom_id_accepted(self):
        custom = uuid.uuid4()
        obj = StubID(id=custom)
        assert obj.id == custom


class TestTimeActionMixin:
    def test_created_at_has_utc_timezone(self):
        obj = StubTimestamp()
        assert obj.created_at.tzinfo == timezone.utc

    def test_updated_at_has_utc_timezone(self):
        obj = StubTimestamp()
        assert obj.updated_at.tzinfo == timezone.utc

    def test_timestamps_are_datetime(self):
        obj = StubTimestamp()
        assert isinstance(obj.created_at, datetime)
        assert isinstance(obj.updated_at, datetime)

    def test_touch_updates_updated_at(self):
        obj = StubTimestamp()
        before = obj.updated_at
        time.sleep(0.005)
        obj.touch()
        assert obj.updated_at > before

    def test_touch_does_not_change_created_at(self):
        obj = StubTimestamp()
        created = obj.created_at
        obj.touch()
        assert obj.created_at == created

    def test_touch_updated_at_is_utc(self):
        obj = StubTimestamp()
        obj.touch()
        assert obj.updated_at.tzinfo == timezone.utc

    def test_multiple_touch_calls_keep_advancing(self):
        obj = StubTimestamp()
        obj.touch()
        first_touch = obj.updated_at
        time.sleep(0.005)
        obj.touch()
        assert obj.updated_at > first_touch
