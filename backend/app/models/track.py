"""Track and related models."""

from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from ..core.database import Base


class Artist(Base):
    """Artist model."""

    __tablename__ = "artists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)

    # External IDs for integrations
    spotify_id = Column(String, unique=True, nullable=True, index=True)
    youtube_channel_id = Column(String, unique=True, nullable=True, index=True)

    # External platform IDs
    external_ids = Column(JSONB, default=dict)  # Other platform IDs

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    tracks = relationship("Track", back_populates="artist")
    metrics = relationship(
        "MetricsDaily", back_populates="artist", cascade="all, delete-orphan"
    )
    breakout_scores = relationship(
        "BreakoutScore", back_populates="artist", cascade="all, delete-orphan"
    )


class Track(Base):
    """Track model."""

    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    duration = Column(Float, nullable=True)  # Duration in seconds

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=True)

    # External IDs
    spotify_id = Column(String, unique=True, nullable=True, index=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="tracks")
    artist = relationship("Artist", back_populates="tracks")
    assets = relationship(
        "TrackAsset",
        back_populates="track",
        cascade="all, delete-orphan",
        uselist=False,
    )
    analyses = relationship(
        "Analysis", back_populates="track", cascade="all, delete-orphan"
    )
    embeddings = relationship(
        "Embedding", back_populates="track", cascade="all, delete-orphan"
    )
    sources = relationship(
        "Source", back_populates="track", cascade="all, delete-orphan"
    )


class TrackAsset(Base):
    """Track assets (audio files, lyrics)."""

    __tablename__ = "track_assets"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False, unique=True)

    # Audio file path
    audio_path = Column(String, nullable=True)
    audio_format = Column(String, nullable=True)  # mp3, wav, etc.

    # Lyrics
    lyrics_text = Column(Text, nullable=True)
    lyrics_source = Column(String, nullable=True)  # "user", "lrclib", "whisper", "user_verified"
    lyrics_confidence = Column(Float, nullable=True)  # 0.0-1.0
    lyrics_language = Column(String, nullable=True)  # "en", "es", etc.
    lyrics_metadata = Column(JSONB, default=dict)  # segments, timestamps, synced_lyrics, etc.

    # Upload metadata
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    track = relationship("Track", back_populates="assets")


class Analysis(Base):
    """Analysis results for a track."""

    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)

    # Sonic Genome (JSONB)
    sonic_genome = Column(JSONB, default=dict)

    # Lyrical Genome (JSONB)
    lyrical_genome = Column(JSONB, default=dict)

    # Hook analysis
    hook_data = Column(JSONB, default=dict)
    
    # TuneScore rating
    tunescore = Column(JSONB, default=dict)
    
    # Genre predictions
    genre_predictions = Column(JSONB, default=dict)
    
    # Quality metrics (pitch accuracy, timing precision, harmonic coherence)
    quality_metrics = Column(JSONB, default=dict)
    
    # Mastering quality (LUFS, Dynamic Range, platform targets)
    mastering_quality = Column(JSONB, default=dict)
    
    # Chord analysis (chord progressions, harmonic complexity)
    chord_analysis = Column(JSONB, default=dict)
    
    # AI lyric critique (Claude-generated feedback and suggestions)
    ai_lyric_critique = Column(JSONB, default=dict)
    
    # AI cost tracking (for transparency and cost governor)
    ai_costs = Column(JSONB, default=dict, comment="Track AI API costs by feature")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    track = relationship("Track", back_populates="analyses")


class Embedding(Base):
    """Vector embeddings for tracks."""

    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False, unique=True)

    # Vector embedding (stored as JSONB for now, pgvector later)
    vector = Column(JSONB, nullable=False)

    # Model version for tracking
    model_version = Column(String, default="MiniLM-L6-v2", nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    track = relationship("Track", back_populates="embeddings")


class Source(Base):
    """External platform sources for tracks."""

    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)

    # Platform info
    platform = Column(String, nullable=False, index=True)  # spotify, youtube, etc.
    external_id = Column(String, nullable=False, index=True)
    url = Column(String, nullable=True)

    # Additional data
    data = Column(JSONB, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    track = relationship("Track", back_populates="sources")


class MetricsDaily(Base):
    """Daily metrics snapshots for artists."""

    __tablename__ = "metrics_daily"

    id = Column(Integer, primary_key=True, index=True)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)

    # Date of snapshot
    date = Column(DateTime, nullable=False, index=True)

    # Platform
    platform = Column(String, nullable=False, index=True)  # spotify, youtube, etc.

    # Metrics (JSONB for flexibility)
    metrics = Column(JSONB, default=dict)
    # Example: {followers: 1000, monthly_listeners: 5000, playlist_adds: 50, views: 10000, etc.}

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    artist = relationship("Artist", back_populates="metrics")


class BreakoutScore(Base):
    """Breakout scores for artists."""

    __tablename__ = "breakout_scores"

    id = Column(Integer, primary_key=True, index=True)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)

    # Score (0-100)
    score = Column(Float, nullable=False, index=True)

    # Rationale (JSONB)
    rationale = Column(JSONB, default=dict)
    # Example: {growth_7d: 0.15, growth_14d: 0.25, playlist_velocity: 10, etc.}

    # Timestamps
    computed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    artist = relationship("Artist", back_populates="breakout_scores")


class Collaboration(Base):
    """Collaboration proposals and impact projections."""

    __tablename__ = "collaborations"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=True)

    # Artist IDs involved (JSONB array)
    artist_ids = Column(JSONB, default=list)

    # Impact projection (JSONB)
    impact_projection = Column(JSONB, default=dict)
    # Example: {estimated_reach: 100000, buzz_score: 85, overlap_percentage: 0.25, etc.}

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    track = relationship("Track")


class CatalogValuation(Base):
    """Catalog valuations and DCF models."""

    __tablename__ = "catalog_valuations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Tracks included (JSONB array of track IDs)
    tracks = Column(JSONB, default=list)

    # DCF model parameters (JSONB)
    dcf_model = Column(JSONB, default=dict)

    # Revenue forecast (JSONB)
    revenue_forecast = Column(JSONB, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User")


# New models for artist intelligence and tracking


class ArtistMetricsSnapshot(Base):
    """Daily snapshots of artist metrics across platforms."""

    __tablename__ = "artist_metrics_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False, index=True)
    snapshot_date = Column(Date, nullable=False, index=True)
    platform = Column(String(50), nullable=False, index=True)  # spotify, youtube, instagram, tiktok

    # Metrics JSONB (platform-specific)
    metrics = Column(JSONB, default=dict)
    # Example: {monthly_listeners: 50000, followers: 10000, engagement_rate: 0.05}

    # Velocity (calculated)
    velocity_7d = Column(Float, nullable=True)
    velocity_28d = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    artist = relationship("Artist")

    __table_args__ = (
        UniqueConstraint("artist_id", "platform", "snapshot_date", name="uq_artist_platform_date"),
        Index("idx_artist_platform_date", "artist_id", "platform", "snapshot_date"),
    )


class PlaylistAppearance(Base):
    """Track which playlists tracks appear on."""

    __tablename__ = "playlist_appearances"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False, index=True)
    playlist_id = Column(String(100), nullable=False, index=True)
    playlist_name = Column(String(500), nullable=True)
    playlist_type = Column(String(50), nullable=True)  # editorial, algorithmic, user
    playlist_followers = Column(Integer, nullable=True)
    position = Column(Integer, nullable=True)
    added_at = Column(DateTime, nullable=False)
    removed_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    track = relationship("Track")

    __table_args__ = (Index("idx_track_playlist", "track_id", "playlist_id"),)


class BreakoutPrediction(Base):
    """Predictive breakout scoring for tracks and artists."""

    __tablename__ = "breakout_predictions"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=True, index=True)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=True, index=True)
    prediction_date = Column(Date, nullable=False, index=True)

    # Breakout Score (0-100)
    breakout_score = Column(Integer, nullable=False)
    confidence = Column(Float, nullable=True)  # 0-1

    # Predictions
    predicted_7d_streams = Column(Integer, nullable=True)
    predicted_14d_streams = Column(Integer, nullable=True)
    predicted_28d_streams = Column(Integer, nullable=True)

    # Explainability
    factors = Column(JSONB, default=dict)  # {velocity: 85, sonic_quality: 92, ...}

    # Post-facto accuracy tracking
    actual_7d_streams = Column(Integer, nullable=True)
    prediction_accuracy = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    track = relationship("Track")
    artist = relationship("Artist")


class ViralAlert(Base):
    """Early viral signal alerts."""

    __tablename__ = "viral_alerts"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)  # tiktok_spike, playlist_momentum, social_surge
    confidence = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    triggered_at = Column(DateTime, nullable=False, index=True)
    outcome = Column(String(50), nullable=True)  # confirmed, false_positive, pending

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    track = relationship("Track")


class TrackTags(Base):
    """AI-generated tags for tracks."""

    __tablename__ = "track_tags"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), unique=True, nullable=False)

    moods = Column(JSONB, default=list)  # [melancholic, uplifting]
    commercial_tags = Column(JSONB, default=list)  # [sync-ready, radio-friendly]
    use_cases = Column(JSONB, default=list)  # [{use_case, confidence, reasoning}]
    sounds_like = Column(JSONB, default=list)  # [Taylor Swift, The Weeknd]

    # Timestamps
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    track = relationship("Track")


class PitchCopy(Base):
    """AI-generated pitch copy for tracks."""

    __tablename__ = "pitch_copy"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), unique=True, nullable=False)

    elevator_pitch = Column(Text, nullable=True)  # 1 sentence
    short_description = Column(Text, nullable=True)  # 2-3 sentences
    sync_pitch = Column(Text, nullable=True)  # licensing-specific

    cost = Column(Float, default=0.0)  # AI generation cost

    # Timestamps
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    track = relationship("Track")


class TrackCredit(Base):
    """Track credits (songwriters, producers, etc.)."""

    __tablename__ = "track_credits"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False, index=True)
    contributor_name = Column(String(500), nullable=False, index=True)
    role = Column(String(100), nullable=True)  # songwriter, producer, mixer
    contribution_pct = Column(Float, nullable=True)  # for royalty splits
    publisher = Column(String(200), nullable=True)
    pro = Column(String(100), nullable=True)  # ASCAP, BMI, SESAC

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    track = relationship("Track")


class CollaboratorProfile(Base):
    """Profile for songwriters/producers."""

    __tablename__ = "collaborator_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), unique=True, nullable=False, index=True)
    role = Column(String(100), nullable=True)
    total_tracks = Column(Integer, default=0)
    avg_tunescore = Column(Float, nullable=True)
    genres = Column(JSONB, default=list)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ArtistCatalogValuation(Base):
    """Catalog valuation for artists."""

    __tablename__ = "artist_catalog_valuations"

    id = Column(Integer, primary_key=True, index=True)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False, index=True)
    valuation_date = Column(Date, nullable=False, index=True)

    annual_revenue = Column(Float, nullable=True)
    valuation_multiple = Column(Float, nullable=True)  # 10-20x
    estimated_value = Column(Float, nullable=True)

    revenue_breakdown = Column(JSONB, default=dict)  # {streaming, sync, performance}
    growth_rate = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    artist = relationship("Artist")
