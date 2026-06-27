"""store_image_keys_instead_of_urls

Revision ID: b3d7a9e2f1c8
Revises: f2b8e4c91a03
Create Date: 2026-06-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = 'b3d7a9e2f1c8'
down_revision: Union[str, Sequence[str], None] = 'f2b8e4c91a03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Используется только в downgrade для восстановления полного URL
_MINIO_PUBLIC_URL = "http://localhost:9000"
_MINIO_BUCKET = "coremarket"


def upgrade() -> None:
    op.execute(
        "UPDATE gallery SET image_url = regexp_replace(image_url, '^https?://[^/]+/[^/]+/', '')"
    )
    op.execute(
        "UPDATE categories SET image_url = regexp_replace(image_url, '^https?://[^/]+/[^/]+/', '') WHERE image_url IS NOT NULL"
    )
    op.execute(
        "UPDATE users SET avatar_url = regexp_replace(avatar_url, '^https?://[^/]+/[^/]+/', '') WHERE avatar_url IS NOT NULL"
    )
    op.execute(
        "UPDATE blog_posts SET cover_image_url = regexp_replace(cover_image_url, '^https?://[^/]+/[^/]+/', '') WHERE cover_image_url IS NOT NULL"
    )


def downgrade() -> None:
    prefix = f"{_MINIO_PUBLIC_URL}/{_MINIO_BUCKET}/"

    op.execute(f"UPDATE gallery SET image_url = '{prefix}' || image_url")
    op.execute(
        f"UPDATE categories SET image_url = '{prefix}' || image_url WHERE image_url IS NOT NULL"
    )
    op.execute(
        f"UPDATE users SET avatar_url = '{prefix}' || avatar_url WHERE avatar_url IS NOT NULL"
    )
    op.execute(
        f"UPDATE blog_posts SET cover_image_url = '{prefix}' || cover_image_url WHERE cover_image_url IS NOT NULL"
    )
