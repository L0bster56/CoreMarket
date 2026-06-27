from enum import Enum


class BlogPostStatus(str, Enum):
    draft = "draft"
    published = "published"
    archived = "archived"
