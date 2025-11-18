"""Pydantic schemas for Industry Pulse API."""

from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class IndustryNewsSchema(BaseModel):
    """Industry news article response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    source: str
    url: str
    summary: Optional[str] = None
    category: Optional[str] = None
    impact_score: Optional[dict[str, int]] = None
    published_at: datetime
    created_at: datetime


class ChartSnapshotSchema(BaseModel):
    """Chart snapshot response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    platform: str
    chart_type: str
    position: int
    track_title: str
    artist: str
    streams: Optional[int] = None
    movement: Optional[int] = None
    spotify_id: Optional[str] = None
    snapshot_date: date
    created_at: datetime


class NewReleaseSchema(BaseModel):
    """New release response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    artist: str
    album_title: str
    release_date: date
    label: Optional[str] = None
    genre: Optional[str] = None
    spotify_id: Optional[str] = None
    apple_music_id: Optional[str] = None
    notable: Optional[bool] = False
    first_day_streams: Optional[int] = None
    extra_data: Optional[dict[str, Any]] = None
    created_at: datetime


class DailyDigestSchema(BaseModel):
    """Daily digest response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    digest_date: date
    summary_text: str
    key_highlights: Optional[dict[str, list[str]]] = None
    cost: Optional[float] = None
    tokens: Optional[dict[str, int]] = None
    generated_at: datetime


class ChartMoversSchema(BaseModel):
    """Chart movers response."""

    risers: list[ChartSnapshotSchema]
    fallers: list[ChartSnapshotSchema]

