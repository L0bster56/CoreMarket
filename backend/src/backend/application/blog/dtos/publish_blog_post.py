from dataclasses import dataclass


@dataclass
class PublishBlogPostCommand:
    slug: str


@dataclass
class UnpublishBlogPostCommand:
    slug: str


@dataclass
class ArchiveBlogPostCommand:
    slug: str
