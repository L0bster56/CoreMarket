from uuid import UUID

from pydantic import BaseModel

from src.backend.domain.tag.entity import Tag


class TagResponse(BaseModel):
    id: UUID
    name: str
    slug: str

    @classmethod
    def from_entity(cls, tag: Tag) -> "TagResponse":
        return cls(
            id=tag.id,
            name=str(tag.name),
            slug=str(tag.slug),
        )


class CreateTagRequest(BaseModel):
    name: str
    slug: str
