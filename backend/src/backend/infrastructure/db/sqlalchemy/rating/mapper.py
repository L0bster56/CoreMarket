from src.backend.domain.rating.entity import Rating
from src.backend.domain.rating.value_objects.score import Score
from src.backend.infrastructure.db.sqlalchemy.rating.model import RatingModel


def to_model(rating: Rating) -> RatingModel:
    return RatingModel(
        id=rating.id,
        item_id=rating.item_id,
        user_id=rating.user_id,
        score=rating.score.value,
        created_at=rating.created_at,
        updated_at=rating.updated_at,
    )


def to_entity(model: RatingModel) -> Rating:
    return Rating(
        id=model.id,
        item_id=model.item_id,
        user_id=model.user_id,
        score=Score(model.score),
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
