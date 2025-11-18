"""add_mastering_quality_to_analyses

Revision ID: 8b047e948aa4
Revises: 2dd3344318de
Create Date: 2025-11-02 07:34:52.469993

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b047e948aa4'
down_revision: Union[str, Sequence[str], None] = '2dd3344318de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add mastering_quality JSONB column to analyses table
    op.add_column(
        'analyses',
        sa.Column('mastering_quality', sa.dialects.postgresql.JSONB, nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove mastering_quality column
    op.drop_column('analyses', 'mastering_quality')
