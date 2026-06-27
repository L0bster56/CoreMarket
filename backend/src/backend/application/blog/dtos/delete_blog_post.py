from dataclasses import dataclass


@dataclass
class DeleteBlogPostCommand:
    slug: str
