"""Pydantic schemas."""

from .track import (
    AnalysisResult,
    AnalysisStatus,
    Artist,
    ArtistCreate,
    EmotionalArcPoint,
    HookData,
    LyricalGenome,
    SonicGenome,
    Track,
    TrackCreate,
    TrackUpdate,
    TrackUpload,
    TrackUploadPayload,
    TrackUploadResponse,
    TrackWithAnalysis,
)

__all__ = [
    "Track",
    "TrackCreate",
    "TrackUpdate",
    "TrackUpload",
    "TrackUploadPayload",
    "TrackUploadResponse",
    "TrackWithAnalysis",
    "Artist",
    "ArtistCreate",
    "SonicGenome",
    "LyricalGenome",
    "HookData",
    "EmotionalArcPoint",
    "AnalysisResult",
    "AnalysisStatus",
]
