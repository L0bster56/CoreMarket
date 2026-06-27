from src.backend.domain.comment.entity import Comment
from src.backend.infrastructure.db.sqlalchemy.comment.model import CommentModel


def to_model(comment: Comment) -> CommentModel:
    return CommentModel(
        id=comment.id,
        item_id=comment.item_id,
        user_id=comment.user_id,
        parent_id=comment.parent_id,
        body=comment.body,
        is_deleted=comment.is_deleted,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
    )


def to_entity(model: CommentModel) -> Comment:
    return Comment(
        id=model.id,
        item_id=model.item_id,
        user_id=model.user_id,
        parent_id=model.parent_id,
        body=model.body,
        is_deleted=model.is_deleted,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
