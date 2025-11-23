"""Industry Pulse data models."""

from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from ..core.database import Base


class IndustryNews(Base):
    """Industry news articles from various sources."""

    __tablename__ = "industry_news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    source = Column(String(100), nullable=False)  # "Billboard", "MBW", etc.
    url = Column(String(1000), nullable=False, unique=True)
    summary = Column(Text)  # AI-generated 2-sentence summary
    category = Column(
        String(50)
    )  # "M&A", "Signings", "Platform", "Legal", "Tech", "Market"
    impact_score = Column(
        JSONB
    )  # {creator: 7, developer: 9, monetizer: 10} - 0-10 scale
    published_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_category_published", "category", "published_at"),
        Index("idx_source_published", "source", "published_at"),
    )


class ChartSnapshot(Base):
    """Daily snapshot of music charts from various platforms."""

    __tablename__ = "chart_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(
        String(50), nullable=False
    )  # "spotify", "apple", "billboard", "youtube"
    chart_type = Column(
        String(100), nullable=False
    )  # "global_top_50", "us_top_100", etc.
    position = Column(Integer, nullable=False)
    track_title = Column(String(500), nullable=False)
    artist = Column(String(500), nullable=False)
    streams = Column(BigInteger)  # if available
    movement = Column(Integer)  # +2, -1, 0 (new entry), null (same position)
    spotify_id = Column(String(100))
    snapshot_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_platform_date", "platform", "snapshot_date"),
        UniqueConstraint("platform", "chart_type", "position", "snapshot_date"),
    )


class NewRelease(Base):
    """New music releases from major platforms."""

    __tablename__ = "new_releases"

    id = Column(Integer, primary_key=True, index=True)
    artist = Column(String(500), nullable=False)
    album_title = Column(String(500), nullable=False)
    release_date = Column(Date, nullable=False)
    label = Column(String(200))
    genre = Column(String(100))
    spotify_id = Column(String(100), unique=True)
    apple_music_id = Column(String(100))
    notable = Column(
        Boolean, default=False
    )  # Major artist flag (>1M followers or editorial pick)
    first_day_streams = Column(BigInteger)  # if available
    extra_data = Column(JSONB)  # Additional platform-specific data (renamed from metadata to avoid conflict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_release_date", "release_date", postgresql_ops={"release_date": "DESC"}),
        Index("idx_notable", "notable"),
    )


class GearRelease(Base):
    """New gear and software releases (Phase 2 - stub for now)."""

    __tablename__ = "gear_releases"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(500), nullable=False)
    manufacturer = Column(String(200), nullable=False)
    category = Column(
        String(100), nullable=False
    )  # "DAW", "Plugin", "Synth", "Interface", "Mic", etc.
    subcategory = Column(String(100))  # "Reverb", "Compressor", "Sampler", etc.
    price = Column(Numeric(10, 2))
    price_tier = Column(String(50))  # "budget" (<$500), "mid" ($500-2K), "pro" (>$2K)
    release_date = Column(Date, nullable=False)
    description = Column(Text)
    url = Column(String(1000))
    image_url = Column(String(1000))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DailyDigest(Base):
    """AI-generated daily digest of industry news and trends."""

    __tablename__ = "daily_digest"

    id = Column(Integer, primary_key=True, index=True)
    digest_date = Column(Date, nullable=False, unique=True)
    summary_text = Column(Text, nullable=False)  # AI-generated executive summary
    key_highlights = Column(
        JSONB
    )  # {creator: [...], developer: [...], monetizer: [...]}
    extra_data = Column(JSONB)  # {opportunities: [...], indie_takeaway: "..."}
    cost = Column(Float)  # AI generation cost
    tokens = Column(JSONB)  # {input: X, output: Y, total: Z}
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_digest_date", "digest_date", postgresql_ops={"digest_date": "DESC"}),
    )


class TrendCluster(Base):
    """Detected sonic/cultural trends (Phase 2 - stub for now)."""

    __tablename__ = "trend_clusters"

    id = Column(Integer, primary_key=True, index=True)
    trend_name = Column(String(200), nullable=False)
    description = Column(Text)
    example_tracks = Column(JSONB)  # [{title, artist, spotify_id}, ...]
    strength_score = Column(Float)  # 0-100 confidence score
    category = Column(String(100))  # "sonic", "lyrical", "cultural", "genre_fusion"
    detected_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("idx_detected_at", "detected_at", postgresql_ops={"detected_at": "DESC"}),)

