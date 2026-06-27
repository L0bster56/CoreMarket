import time
import uuid

import pytest

from src.backend.domain.comment.entity import Comment


def make_comment(**kwargs) -> Comment:
    defaults = dict(
        item_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        parent_id=None,
        body="Отличный товар!",
    )
    defaults.update(kwargs)
    return Comment.create(**defaults)


class TestCommentCreate:
    def test_create_sets_all_fields(self):
        item_id = uuid.uuid4()
        user_id = uuid.uuid4()
        comment = Comment.create(
            item_id=item_id,
            user_id=user_id,
            parent_id=None,
            body="Отличный товар!",
        )
        assert comment.item_id == item_id
        assert comment.user_id == user_id
        assert comment.parent_id is None
        assert comment.body == "Отличный товар!"
        assert comment.is_deleted is False

    def test_create_with_parent_id(self):
        parent_id = uuid.uuid4()
        comment = make_comment(parent_id=parent_id)
        assert comment.parent_id == parent_id

    def test_create_gives_unique_ids(self):
        c1 = make_comment()
        c2 = make_comment()
        assert c1.id != c2.id

    def test_id_is_uuid(self):
        comment = make_comment()
        assert isinstance(comment.id, uuid.UUID)

    def test_timestamps_are_utc(self):
        from datetime import timezone
        comment = make_comment()
        assert comment.created_at.tzinfo == timezone.utc
        assert comment.updated_at.tzinfo == timezone.utc

    def test_is_deleted_default_false(self):
        comment = make_comment()
        assert comment.is_deleted is False


class TestCommentSoftDelete:
    def test_soft_delete_sets_is_deleted(self):
        comment = make_comment()
        comment.soft_delete()
        assert comment.is_deleted is True

    def test_soft_delete_calls_touch(self):
        comment = make_comment()
        before = comment.updated_at
        time.sleep(0.005)
        comment.soft_delete()
        assert comment.updated_at > before

    def test_soft_delete_does_not_remove_body(self):
        comment = make_comment(body="Отличный товар!")
        comment.soft_delete()
        assert comment.body == "Отличный товар!"


class TestCommentChangeBody:
    def test_change_body_updates_field(self):
        comment = make_comment(body="Старый текст")
        comment.change_body("Новый текст")
        assert comment.body == "Новый текст"

    def test_change_body_calls_touch(self):
        comment = make_comment()
        before = comment.updated_at
        time.sleep(0.005)
        comment.change_body("Updated body")
        assert comment.updated_at > before


class TestCommentEquality:
    def test_same_id_equal(self):
        uid = uuid.uuid4()
        item_id = uuid.uuid4()
        user_id = uuid.uuid4()
        from datetime import datetime, timezone
        c1 = Comment(
            id=uid, item_id=item_id, user_id=user_id,
            parent_id=None, body="body1",
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        c2 = Comment(
            id=uid, item_id=item_id, user_id=user_id,
            parent_id=None, body="body2",
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        assert c1 == c2

    def test_different_id_not_equal(self):
        c1 = make_comment()
        c2 = make_comment()
        assert c1 != c2
