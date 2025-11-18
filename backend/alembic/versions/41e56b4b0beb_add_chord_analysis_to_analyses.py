"""add_chord_analysis_to_analyses

Revision ID: 41e56b4b0beb
Revises: 8b047e948aa4
Create Date: 2025-11-02 09:51:40.836616

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '41e56b4b0beb'
down_revision: Union[str, Sequence[str], None] = '8b047e948aa4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add chord_analysis JSONB column to analyses table
    op.add_column(
        'analyses',
        sa.Column('chord_analysis', sa.dialects.postgresql.JSONB, nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove chord_analysis column
    op.drop_column('analyses', 'chord_analysis')
