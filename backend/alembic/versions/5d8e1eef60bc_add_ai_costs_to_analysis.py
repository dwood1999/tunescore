"""add_ai_costs_to_analysis

Revision ID: 5d8e1eef60bc
Revises: f33fc2e17967
Create Date: 2025-11-04 10:00:06.983346

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '5d8e1eef60bc'
down_revision: Union[str, Sequence[str], None] = 'f33fc2e17967'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add ai_costs column to analyses table
    op.add_column(
        'analyses',
        sa.Column(
            'ai_costs',
            postgresql.JSONB(astext_type=sa.Text()),
            server_default='{}',
            nullable=True,
            comment="Track AI API costs by feature"
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove ai_costs column from analyses table
    op.drop_column('analyses', 'ai_costs')
