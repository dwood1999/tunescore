"""add_ai_lyric_critique_to_analyses

Revision ID: 1f4811637e38
Revises: 41e56b4b0beb
Create Date: 2025-11-02 09:58:22.458215

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f4811637e38'
down_revision: Union[str, Sequence[str], None] = '41e56b4b0beb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add ai_lyric_critique JSONB column to analyses table
    op.add_column(
        'analyses',
        sa.Column('ai_lyric_critique', sa.dialects.postgresql.JSONB, nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove ai_lyric_critique column
    op.drop_column('analyses', 'ai_lyric_critique')
