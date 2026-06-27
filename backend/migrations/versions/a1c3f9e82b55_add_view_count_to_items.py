"""add_view_count_to_items

Revision ID: a1c3f9e82b55
Revises: de06aeaed17c
Create Date: 2026-06-20 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1c3f9e82b55'
down_revision: Union[str, Sequence[str], None] = 'de06aeaed17c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'items',
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('items', 'view_count')
