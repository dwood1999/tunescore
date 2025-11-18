"""Track-related Pydantic schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TrackUploadPayload(BaseModel):
    """Payload schema for track upload metadata."""

    title: str = Field(..., min_length=1, max_length=255)
    artist_name: str | None = Field(default=None, max_length=255)
    genre: str | None = Field(default=None, max_length=255)
    lyrics: str | None = None
    auto_transcribe: bool = Field(default=True, description="Auto-transcribe lyrics if not provided")
    verify_lyrics: bool = Field(default=False, description="Verify provided lyrics against audio")


# Track schemas
class TrackBase(BaseModel):
    """Base track schema."""

    title: str = Field(..., min_length=1, max_length=255)
    duration: float | None = None
    artist_id: int | None = None


class TrackCreate(TrackBase):
    """Schema for creating a track."""


class TrackUpdate(BaseModel):
    """Schema for updating a track."""

    title: str | None = Field(None, min_length=1, max_length=255)
    duration: float | None = None
    artist_id: int | None = None


class TrackUpload(BaseModel):
    """Schema for track upload with audio and lyrics."""

    title: str = Field(..., min_length=1, max_length=255)
    artist_name: str | None = None
    lyrics: str | None = None


class Track(TrackBase):
    """Track schema with full details."""

    id: int
    user_id: int
    spotify_id: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Analysis schemas
class SonicGenome(BaseModel):
    """Sonic genome analysis results."""

    duration: float
    tempo: float
    key: int
    key_name: str
    spectral_centroid_mean: float
    spectral_centroid_std: float
    rms_mean: float
    loudness: float
    energy: float
    danceability: float
    valence: float
    acousticness: float


class HookData(BaseModel):
    """Hook detection results."""

    start_time: float
    end_time: float
    duration: float
    hook_score: float
    rationale: str


class EmotionalArcPoint(BaseModel):
    """Single point in emotional arc."""

    line_index: int
    positive: float
    negative: float
    neutral: float
    compound: float


class LyricalGenome(BaseModel):
    """Lyrical genome analysis results."""

    overall_sentiment: dict[str, Any]
    emotional_arc: list[EmotionalArcPoint]
    structure: dict[str, Any]
    themes: list[str]
    complexity: dict[str, Any]
    repetition: dict[str, Any]
    line_count: int
    word_count: int


class TranscriptionResult(BaseModel):
    """Lyrics transcription result."""
    
    text: str
    language: str
    confidence: float
    success: bool
    verified: bool = False
    verification: dict[str, Any] | None = None


class AnalysisResult(BaseModel):
    """Complete analysis result."""

    track_id: int
    sonic_genome: dict[str, Any] | None = None
    lyrical_genome: dict[str, Any] | None = None
    hook_data: dict[str, Any] | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class TrackWithAnalysis(Track):
    """Track with analysis data."""

    artist_name: str | None = None
    sonic_genome: dict[str, Any] | None = None
    lyrical_genome: dict[str, Any] | None = None
    hook_data: dict[str, Any] | None = None
    tunescore: dict[str, Any] | None = None
    genre_predictions: dict[str, Any] | None = None
    quality_metrics: dict[str, Any] | None = None
    mastering_quality: dict[str, Any] | None = None
    chord_analysis: dict[str, Any] | None = None
    ai_lyric_critique: dict[str, Any] | None = None
    ai_tags: dict[str, Any] | None = None
    ai_pitch: dict[str, Any] | None = None
    track_tags: dict[str, Any] | None = None  # Alias for frontend
    pitch_copy: dict[str, Any] | None = None  # Alias for frontend
    lyrics: str | None = None
    lyrics_source: str | None = None  # "user", "lrclib", "whisper", "user_verified"
    lyrics_confidence: float | None = None
    lyrics_language: str | None = None
    lyrics_metadata: dict[str, Any] | None = None


# Artist schemas
class ArtistBase(BaseModel):
    """Base artist schema."""

    name: str = Field(..., min_length=1, max_length=255)
    spotify_id: str | None = None
    youtube_channel_id: str | None = None


class ArtistCreate(ArtistBase):
    """Schema for creating an artist."""


class Artist(ArtistBase):
    """Artist schema with full details."""

    id: int
    external_ids: dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Response schemas
class TrackUploadResponse(BaseModel):
    """Response after track upload."""

    track: Track
    analysis_started: bool
    message: str
    transcription: TranscriptionResult | None = None


class AnalysisStatus(BaseModel):
    """Analysis status response."""

    track_id: int
    status: str  # pending, processing, completed, failed
    sonic_genome_complete: bool
    lyrical_genome_complete: bool
    hook_detection_complete: bool
    error: str | None = None
