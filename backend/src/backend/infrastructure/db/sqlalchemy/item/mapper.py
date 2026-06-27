from __future__ import annotations

from src.backend.domain.category.value_objects.slug.value_object import Slug
from src.backend.domain.item.characteristic import Characteristic
from src.backend.domain.item.entity import Item
from src.backend.domain.item.gallery import Gallery
from src.backend.domain.item.value_objects.marketplace_link import MarketplaceLink
from src.backend.domain.shared.value_objects.name.value_object import Name
from src.backend.domain.tag.entity import Tag
from src.backend.infrastructure.db.sqlalchemy.item.model import CharacteristicModel, GalleryModel, ItemModel
from src.backend.infrastructure.db.sqlalchemy.tag.model import TagModel


def _links_to_json(links: list[MarketplaceLink]) -> list[dict]:
    return [{"name": str(link.name), "url": link.url, "price": link.price} for link in links]


def _json_to_links(data: list[dict] | None) -> list[MarketplaceLink]:
    if not data:
        return []
    return [MarketplaceLink(name=Name(d["name"]), url=d["url"], price=d.get("price")) for d in data]


def item_to_model(item: Item) -> ItemModel:
    return ItemModel(
        id=item.id,
        name=str(item.name),
        short_description=item.short_description,
        description=item.description,
        category_id=item.category_id,
        youtube_url=item.youtube_url,
        marketplace_links=_links_to_json(item.marketplace_links),
        is_published=item.is_published,
        view_count=item.view_count,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def item_to_entity(model: ItemModel) -> Item:
    return Item(
        id=model.id,
        name=Name(model.name),
        short_description=model.short_description,
        description=model.description,
        category_id=model.category_id,
        youtube_url=model.youtube_url,
        marketplace_links=_json_to_links(model.marketplace_links),
        is_published=model.is_published,
        view_count=model.view_count,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def characteristic_to_model(c: Characteristic) -> CharacteristicModel:
    return CharacteristicModel(
        id=c.id,
        item_id=c.item_id,
        group=c.group,
        name=c.name,
        value=c.value,
    )


def characteristic_to_entity(model: CharacteristicModel) -> Characteristic:
    return Characteristic(
        id=model.id,
        item_id=model.item_id,
        group=model.group,
        name=model.name,
        value=model.value,
    )


def gallery_to_model(g: Gallery) -> GalleryModel:
    return GalleryModel(
        id=g.id,
        item_id=g.item_id,
        image_url=g.image_url,
    )


def gallery_to_entity(model: GalleryModel) -> Gallery:
    return Gallery(
        id=model.id,
        item_id=model.item_id,
        image_url=model.image_url,
    )


def tag_to_entity(model: TagModel) -> Tag:
    return Tag(
        id=model.id,
        name=Name(model.name),
        slug=Slug(model.slug),
    )
