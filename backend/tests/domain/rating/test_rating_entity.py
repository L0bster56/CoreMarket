import time
import uuid

import pytest

from src.backend.domain.rating.entity import Rating
from src.backend.domain.rating.error import InvalidScoreError
from src.backend.domain.rating.value_objects.score import Score


def make_rating(score: int = 4) -> Rating:
    return Rating.create(
        item_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        score=Score(score),
    )


class TestRatingCreate:
    def test_create_sets_all_fields(self):
        item_id = uuid.uuid4()
        user_id = uuid.uuid4()
        rating = Rating.create(item_id=item_id, user_id=user_id, score=Score(5))
        assert rating.item_id == item_id
        assert rating.user_id == user_id
        assert rating.score.value == 5

    def test_create_gives_unique_ids(self):
        r1 = make_rating(3)
        r2 = make_rating(5)
        assert r1.id != r2.id

    def test_id_is_uuid(self):
        rating = make_rating()
        assert isinstance(rating.id, uuid.UUID)

    def test_timestamps_are_utc(self):
        from datetime import timezone
        rating = make_rating()
        assert rating.created_at.tzinfo == timezone.utc
        assert rating.updated_at.tzinfo == timezone.utc

    @pytest.mark.parametrize("score", [1, 2, 3, 4, 5])
    def test_create_with_all_valid_scores(self, score):
        rating = make_rating(score)
        assert rating.score.value == score


class TestRatingUpdate:
    def test_update_changes_score(self):
        rating = make_rating(3)
        rating.update(5)
        assert rating.score.value == 5

    def test_update_calls_touch(self):
        rating = make_rating(3)
        before = rating.updated_at
        time.sleep(0.005)
        rating.update(5)
        assert rating.updated_at > before

    def test_update_with_invalid_score_raises(self):
        rating = make_rating(3)
        with pytest.raises(InvalidScoreError):
            rating.update(-1)

    def test_update_preserves_item_and_user_ids(self):
        item_id = uuid.uuid4()
        user_id = uuid.uuid4()
        rating = Rating.create(item_id=item_id, user_id=user_id, score=Score(3))
        rating.update(5)
        assert rating.item_id == item_id
        assert rating.user_id == user_id


class TestRatingEquality:
    def test_same_id_equal(self):
        uid = uuid.uuid4()
        item_id = uuid.uuid4()
        user_id = uuid.uuid4()
        from datetime import datetime, timezone
        r1 = Rating(
            id=uid, item_id=item_id, user_id=user_id, score=Score(3),
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        r2 = Rating(
            id=uid, item_id=item_id, user_id=user_id, score=Score(5),
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        assert r1 == r2

    def test_different_id_not_equal(self):
        r1 = make_rating(3)
        r2 = make_rating(3)
        assert r1 != r2
