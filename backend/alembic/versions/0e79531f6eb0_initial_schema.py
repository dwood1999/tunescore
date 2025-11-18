"""Initial schema

Revision ID: 0e79531f6eb0
Revises: 
Create Date: 2025-10-30 23:29:25.760597

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0e79531f6eb0'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Enable pg_trgm extension
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('tier', sa.String(), nullable=True, server_default='free'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    
    # Create artists table
    op.create_table(
        'artists',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('spotify_id', sa.String(), nullable=True),
        sa.Column('youtube_channel_id', sa.String(), nullable=True),
        sa.Column('external_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_artists_id'), 'artists', ['id'], unique=False)
    op.create_index(op.f('ix_artists_name'), 'artists', ['name'], unique=False)
    op.create_index(op.f('ix_artists_spotify_id'), 'artists', ['spotify_id'], unique=True)
    op.create_index(op.f('ix_artists_youtube_channel_id'), 'artists', ['youtube_channel_id'], unique=True)
    
    # Create tracks table
    op.create_table(
        'tracks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('duration', sa.Float(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('artist_id', sa.Integer(), nullable=True),
        sa.Column('spotify_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['artist_id'], ['artists.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tracks_id'), 'tracks', ['id'], unique=False)
    op.create_index(op.f('ix_tracks_spotify_id'), 'tracks', ['spotify_id'], unique=True)
    op.create_index(op.f('ix_tracks_title'), 'tracks', ['title'], unique=False)
    
    # Create track_assets table
    op.create_table(
        'track_assets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('track_id', sa.Integer(), nullable=False),
        sa.Column('audio_path', sa.String(), nullable=True),
        sa.Column('audio_format', sa.String(), nullable=True),
        sa.Column('lyrics_text', sa.Text(), nullable=True),
        sa.Column('upload_date', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['track_id'], ['tracks.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('track_id')
    )
    op.create_index(op.f('ix_track_assets_id'), 'track_assets', ['id'], unique=False)
    
    # Create analyses table
    op.create_table(
        'analyses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('track_id', sa.Integer(), nullable=False),
        sa.Column('sonic_genome', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('lyrical_genome', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('hook_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['track_id'], ['tracks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analyses_id'), 'analyses', ['id'], unique=False)
    
    # Create embeddings table
    op.create_table(
        'embeddings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('track_id', sa.Integer(), nullable=False),
        sa.Column('vector', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('model_version', sa.String(), nullable=False, server_default='MiniLM-L6-v2'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['track_id'], ['tracks.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('track_id')
    )
    op.create_index(op.f('ix_embeddings_id'), 'embeddings', ['id'], unique=False)
    
    # Create sources table
    op.create_table(
        'sources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('track_id', sa.Integer(), nullable=False),
        sa.Column('platform', sa.String(), nullable=False),
        sa.Column('external_id', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=True),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['track_id'], ['tracks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sources_external_id'), 'sources', ['external_id'], unique=False)
    op.create_index(op.f('ix_sources_id'), 'sources', ['id'], unique=False)
    op.create_index(op.f('ix_sources_platform'), 'sources', ['platform'], unique=False)
    
    # Create metrics_daily table
    op.create_table(
        'metrics_daily',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('artist_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('platform', sa.String(), nullable=False),
        sa.Column('metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['artist_id'], ['artists.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_metrics_daily_date'), 'metrics_daily', ['date'], unique=False)
    op.create_index(op.f('ix_metrics_daily_id'), 'metrics_daily', ['id'], unique=False)
    op.create_index(op.f('ix_metrics_daily_platform'), 'metrics_daily', ['platform'], unique=False)
    
    # Create breakout_scores table
    op.create_table(
        'breakout_scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('artist_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('rationale', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('computed_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['artist_id'], ['artists.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_breakout_scores_computed_at'), 'breakout_scores', ['computed_at'], unique=False)
    op.create_index(op.f('ix_breakout_scores_id'), 'breakout_scores', ['id'], unique=False)
    op.create_index(op.f('ix_breakout_scores_score'), 'breakout_scores', ['score'], unique=False)
    
    # Create collaborations table
    op.create_table(
        'collaborations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('track_id', sa.Integer(), nullable=True),
        sa.Column('artist_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'),
        sa.Column('impact_projection', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['track_id'], ['tracks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_collaborations_id'), 'collaborations', ['id'], unique=False)
    
    # Create catalog_valuations table
    op.create_table(
        'catalog_valuations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('tracks', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'),
        sa.Column('dcf_model', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('revenue_forecast', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_catalog_valuations_id'), 'catalog_valuations', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_catalog_valuations_id'), table_name='catalog_valuations')
    op.drop_table('catalog_valuations')
    op.drop_index(op.f('ix_collaborations_id'), table_name='collaborations')
    op.drop_table('collaborations')
    op.drop_index(op.f('ix_breakout_scores_score'), table_name='breakout_scores')
    op.drop_index(op.f('ix_breakout_scores_id'), table_name='breakout_scores')
    op.drop_index(op.f('ix_breakout_scores_computed_at'), table_name='breakout_scores')
    op.drop_table('breakout_scores')
    op.drop_index(op.f('ix_metrics_daily_platform'), table_name='metrics_daily')
    op.drop_index(op.f('ix_metrics_daily_id'), table_name='metrics_daily')
    op.drop_index(op.f('ix_metrics_daily_date'), table_name='metrics_daily')
    op.drop_table('metrics_daily')
    op.drop_index(op.f('ix_sources_platform'), table_name='sources')
    op.drop_index(op.f('ix_sources_id'), table_name='sources')
    op.drop_index(op.f('ix_sources_external_id'), table_name='sources')
    op.drop_table('sources')
    op.drop_index(op.f('ix_embeddings_id'), table_name='embeddings')
    op.drop_table('embeddings')
    op.drop_index(op.f('ix_analyses_id'), table_name='analyses')
    op.drop_table('analyses')
    op.drop_index(op.f('ix_track_assets_id'), table_name='track_assets')
    op.drop_table('track_assets')
    op.drop_index(op.f('ix_tracks_title'), table_name='tracks')
    op.drop_index(op.f('ix_tracks_spotify_id'), table_name='tracks')
    op.drop_index(op.f('ix_tracks_id'), table_name='tracks')
    op.drop_table('tracks')
    op.drop_index(op.f('ix_artists_youtube_channel_id'), table_name='artists')
    op.drop_index(op.f('ix_artists_spotify_id'), table_name='artists')
    op.drop_index(op.f('ix_artists_name'), table_name='artists')
    op.drop_index(op.f('ix_artists_id'), table_name='artists')
    op.drop_table('artists')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
