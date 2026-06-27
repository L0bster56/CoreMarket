"""add_blog_tables

Revision ID: c7e3a1d09f44
Revises: a1c3f9e82b55
Create Date: 2026-06-20 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c7e3a1d09f44'
down_revision: Union[str, Sequence[str], None] = 'a1c3f9e82b55'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'blog_categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False),
        sa.Column('catalog_category_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_blog_categories_slug', 'blog_categories', ['slug'], unique=True)

    op.create_table(
        'blog_tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_blog_tags_slug', 'blog_tags', ['slug'], unique=True)

    op.create_table(
        'blog_posts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('slug', sa.String(500), nullable=False),
        sa.Column('short_description', sa.String(1000), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('cover_image_url', sa.String(500), nullable=True),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='draft'),
        sa.Column('seo_title', sa.String(255), nullable=True),
        sa.Column('seo_description', sa.String(500), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['blog_categories.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_blog_posts_slug', 'blog_posts', ['slug'], unique=True)
    op.create_index('ix_blog_posts_status_created_at', 'blog_posts', ['status', 'created_at'])

    op.create_table(
        'blog_post_tags',
        sa.Column('blog_post_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('blog_tag_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['blog_post_id'], ['blog_posts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['blog_tag_id'], ['blog_tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('blog_post_id', 'blog_tag_id'),
    )

    op.create_table(
        'blog_product_links',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('blog_post_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['blog_post_id'], ['blog_posts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('blog_product_links')
    op.drop_table('blog_post_tags')
    op.drop_index('ix_blog_posts_status_created_at', table_name='blog_posts')
    op.drop_index('ix_blog_posts_slug', table_name='blog_posts')
    op.drop_table('blog_posts')
    op.drop_index('ix_blog_tags_slug', table_name='blog_tags')
    op.drop_table('blog_tags')
    op.drop_index('ix_blog_categories_slug', table_name='blog_categories')
    op.drop_table('blog_categories')
