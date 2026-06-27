"""blog_posts_use_catalog_categories

Revision ID: f2b8e4c91a03
Revises: c7e3a1d09f44
Create Date: 2026-06-20 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'f2b8e4c91a03'
down_revision: Union[str, Sequence[str], None] = 'c7e3a1d09f44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('blog_posts_category_id_fkey', 'blog_posts', type_='foreignkey')
    op.create_foreign_key(
        'blog_posts_category_id_fkey',
        'blog_posts', 'categories',
        ['category_id'], ['id'],
        ondelete='SET NULL',
    )
    op.drop_index('ix_blog_categories_slug', table_name='blog_categories')
    op.drop_table('blog_categories')


def downgrade() -> None:
    op.create_table(
        'blog_categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False),
        sa.Column('catalog_category_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_blog_categories_slug', 'blog_categories', ['slug'], unique=True)
    op.drop_constraint('blog_posts_category_id_fkey', 'blog_posts', type_='foreignkey')
    op.create_foreign_key(
        'blog_posts_category_id_fkey',
        'blog_posts', 'blog_categories',
        ['category_id'], ['id'],
        ondelete='SET NULL',
    )
