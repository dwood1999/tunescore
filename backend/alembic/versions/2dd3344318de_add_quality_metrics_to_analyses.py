"""add_quality_metrics_to_analyses

Revision ID: 2dd3344318de
Revises: 23512442cf40
Create Date: 2025-11-01 12:06:19.554175

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2dd3344318de'
down_revision: Union[str, Sequence[str], None] = '23512442cf40'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('analyses', sa.Column('quality_metrics', sa.dialects.postgresql.JSONB(), nullable=True))
    # Set default empty dict for existing rows
    op.execute("UPDATE analyses SET quality_metrics = '{}'::jsonb WHERE quality_metrics IS NULL")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('analyses', 'quality_metrics')
