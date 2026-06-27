from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class CreateBlogPostCommand:
    title: str
    slug: str
    short_description: str | None = None


@dataclass
class CreateBlogPostResult:
    id: UUID
    title: str
    slug: str
    short_description: str | None
    status: str
    created_at: datetime
    updated_at: datetime
