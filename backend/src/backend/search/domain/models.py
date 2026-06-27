from dataclasses import dataclass, field


@dataclass
class SearchHit:
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


@dataclass
class SearchResponse:
    hits: list[SearchHit]
    total: int
    took_ms: int
    query: str | None
    page: int
    page_size: int


@dataclass
class SuggestionItem:
    id: str
    title: str
    score: float


@dataclass
class SuggestionsResponse:
    suggestions: list[SuggestionItem] = field(default_factory=list)
    query: str = ""
