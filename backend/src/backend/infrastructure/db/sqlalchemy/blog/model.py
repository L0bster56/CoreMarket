from sqlalchemy import Column, Integer, String, Text, UUID, ForeignKey, Table, Index
from sqlalchemy.orm import relationship

from src.backend.infrastructure.db.sqlalchemy.core.mixins import UUIDMixin, TimeStampMixin
from src.backend.infrastructure.db.sqlalchemy.core.models import Base


blog_post_tags = Table(
    'blog_post_tags',
    Base.metadata,
    Column('blog_post_id', UUID(as_uuid=True), ForeignKey('blog_posts.id', ondelete='CASCADE'), primary_key=True),
    Column('blog_tag_id', UUID(as_uuid=True), ForeignKey('blog_tags.id', ondelete='CASCADE'), primary_key=True),
)


class BlogTagModel(Base, UUIDMixin):
    __tablename__ = 'blog_tags'

    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False)

    __table_args__ = (
        Index('ix_blog_tags_slug', 'slug', unique=True),
    )


class BlogProductLinkModel(Base, UUIDMixin):
    __tablename__ = 'blog_product_links'

    blog_post_id = Column(UUID(as_uuid=True), ForeignKey('blog_posts.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(UUID(as_uuid=True), nullable=False)
    display_order = Column(Integer, default=0, nullable=False)


class BlogPostModel(Base, UUIDMixin, TimeStampMixin):
    __tablename__ = 'blog_posts'

    title = Column(String(500), nullable=False)
    slug = Column(String(500), nullable=False)
    short_description = Column(String(1000), nullable=True)
    content = Column(Text, nullable=True)
    cover_image_url = Column(String(500), nullable=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    status = Column(String(50), nullable=False, default='draft')
    seo_title = Column(String(255), nullable=True)
    seo_description = Column(String(500), nullable=True)

    tags = relationship(
        'BlogTagModel',
        secondary=blog_post_tags,
        backref='posts',
        lazy='selectin',
    )
    product_links = relationship(
        'BlogProductLinkModel',
        backref='post',
        lazy='selectin',
        cascade='all, delete-orphan',
    )

    __table_args__ = (
        Index('ix_blog_posts_slug', 'slug', unique=True),
        Index('ix_blog_posts_status_created_at', 'status', 'created_at'),
    )
