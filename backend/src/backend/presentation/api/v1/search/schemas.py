from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SearchItemHit(BaseModel):
    id: str
    title: str
    short_description: str
    category_id: str
    tags: list[str]
    rating_avg: float
    view_count: int
    is_published: bool
    created_at: str | None
    updated_at: str | None
    preview_image_key: str | None
    score: float


class SearchItemsResponse(BaseModel):
    hits: list[SearchItemHit]
    total: int
    took_ms: int
    query: str | None
    page: int
    page_size: int


class SuggestionItemSchema(BaseModel):
    id: str
    title: str
    score: float


class SuggestionsResponse(BaseModel):
    suggestions: list[SuggestionItemSchema]
    query: str


class ReindexResponse(BaseModel):
    indexed: int
    message: str
