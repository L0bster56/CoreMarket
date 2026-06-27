import logging
import math
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.infrastructure.db.sqlalchemy.category.model import CategoryModel
from src.backend.infrastructure.db.sqlalchemy.item.model import (
    GalleryModel,
    ItemModel,
    item_tags,
)
from src.backend.infrastructure.db.sqlalchemy.rating.model import RatingModel
from src.backend.infrastructure.db.sqlalchemy.tag.model import TagModel

logger = logging.getLogger("coremarket.search.sync")


async def build_item_document(item_id: UUID, session: AsyncSession) -> dict | None:
    stmt = select(ItemModel).where(ItemModel.id == item_id)
    result = await session.execute(stmt)
    item = result.scalar_one_or_none()
    if item is None:
        return None

    category_name: str | None = None
    if item.category_id:
        cat_stmt = select(CategoryModel.name).where(CategoryModel.id == item.category_id)
        cat_result = await session.execute(cat_stmt)
        category_name = cat_result.scalar_one_or_none()

    tags_stmt = (
        select(TagModel.slug, TagModel.name)
        .join(item_tags, TagModel.id == item_tags.c.tag_id)
        .where(item_tags.c.item_id == item_id)
    )
    tags_result = await session.execute(tags_stmt)
    tag_rows = tags_result.all()
    tag_slugs = [r.slug for r in tag_rows]
    tag_names_list = [r.name for r in tag_rows]

    rating_stmt = (
        select(func.avg(RatingModel.score).label("avg"))
        .where(RatingModel.item_id == item_id)
    )
    rating_result = await session.execute(rating_stmt)
    avg_rating = float(rating_result.scalar_one_or_none() or 0.0)

    gallery_stmt = (
        select(GalleryModel.image_url)
        .where(GalleryModel.item_id == item_id)
        .order_by(GalleryModel.id)
        .limit(1)
    )
    gallery_result = await session.execute(gallery_stmt)
    preview_image_key: str | None = gallery_result.scalar_one_or_none()

    characteristics = [
        {"name": c.name, "value": c.value, "group": c.group}
        for c in item.characteristics
    ]

    return {
        "id": str(item.id),
        "title": item.name,
        "short_description": item.short_description,
        "description": item.description,
        "category_id": str(item.category_id),
        "category_name": category_name,
        "tags": tag_slugs,
        "tag_names": " ".join(tag_names_list),
        "rating_avg": avg_rating,
        "view_count": item.view_count,
        "is_published": item.is_published,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "updated_at": item.updated_at.isoformat() if item.updated_at else None,
        "characteristics": characteristics,
        "popularity_score": _popularity_score(avg_rating, item.view_count),
        "preview_image_key": preview_image_key,
        "marketplace_links": item.marketplace_links,
    }


async def index_item(
    item_id: UUID,
    session: AsyncSession,
    es: AsyncElasticsearch,
    index_name: str,
) -> bool:
    doc = await build_item_document(item_id, session)
    if doc is None:
        logger.warning("search_index_skip_missing", extra={"item_id": str(item_id)})
        return False
    await es.index(index=index_name, id=str(item_id), document=doc)
    logger.info("search_item_indexed", extra={"item_id": str(item_id)})
    return True


async def delete_item_from_index(
    item_id: str,
    es: AsyncElasticsearch,
    index_name: str,
) -> None:
    await es.delete(index=index_name, id=item_id, ignore_status=404)
    logger.info("search_item_deleted", extra={"item_id": item_id})


async def bulk_reindex(
    session: AsyncSession,
    es: AsyncElasticsearch,
    index_name: str,
) -> int:
    stmt = select(ItemModel.id)
    result = await session.execute(stmt)
    item_ids = [row.id for row in result.all()]

    if not item_ids:
        return 0

    indexed = 0
    batch_size = 100

    for batch_start in range(0, len(item_ids), batch_size):
        batch = item_ids[batch_start : batch_start + batch_size]
        operations: list = []

        for item_id in batch:
            doc = await build_item_document(item_id, session)
            if doc is None:
                continue
            operations.append({"index": {"_index": index_name, "_id": str(item_id)}})
            operations.append(doc)

        if operations:
            response = await es.bulk(operations=operations)
            if response.get("errors"):
                for item_resp in response["items"]:
                    if "error" in item_resp.get("index", {}):
                        logger.error(
                            "bulk_index_error",
                            extra={"error": item_resp["index"]["error"]},
                        )
            indexed += len(operations) // 2

        logger.info(
            "bulk_reindex_batch",
            extra={"batch_start": batch_start, "indexed": indexed},
        )

    logger.info("bulk_reindex_complete", extra={"total": indexed, "index": index_name})
    return indexed


def _popularity_score(rating_avg: float, view_count: int) -> float:
    return round(rating_avg * 0.6 + math.log1p(view_count) * 0.4, 4)
