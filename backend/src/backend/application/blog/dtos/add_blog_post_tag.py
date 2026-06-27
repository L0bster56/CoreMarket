from dataclasses import dataclass
from uuid import UUID


@dataclass
class AddBlogPostTagCommand:
    slug: str
    tag_id: UUID


@dataclass
class RemoveBlogPostTagCommand:
    slug: str
    tag_id: UUID
