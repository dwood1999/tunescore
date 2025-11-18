"""API routes for AI tagging and pitch generation."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...models import Artist
from ...models.track import Track, Analysis, TrackTags, PitchCopy
from ...services.ai_tagging.mood_classifier import MoodClassifier
from ...services.ai_tagging.pitch_generator import PitchGenerator

router = APIRouter(prefix="/tracks", tags=["AI Tagging"])
logger = logging.getLogger(__name__)


@router.post("/{track_id}/generate-tags")
async def generate_tags(
    track_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Generate AI tags for a track."""
    # Get track with analysis
    result = await db.execute(
        select(Track, Analysis)
        .join(Analysis, Track.id == Analysis.track_id)
        .where(Track.id == track_id)
    )
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="Track or analysis not found")

    track, analysis = row

    if not analysis.sonic_genome:
        raise HTTPException(status_code=400, detail="Sonic genome not available for this track.")

    # Generate tags using mood classifier
    classifier = MoodClassifier()
    try:
        mood_data = classifier.classify(analysis.sonic_genome, analysis.lyrical_genome)

        commercial_tags = classifier.classify_commercial_tags(analysis.sonic_genome)

        result = await db.execute(select(TrackTags).where(TrackTags.track_id == track_id))
        track_tags_db = result.scalar_one_or_none()

        if track_tags_db:
            track_tags_db.moods = mood_data.get("moods", [])
            track_tags_db.commercial_tags = commercial_tags
            track_tags_db.use_cases = mood_data.get("use_cases", [])
            track_tags_db.sounds_like = mood_data.get("sounds_like", [])
        else:
            track_tags_db = TrackTags(
                track_id=track_id,
                moods=mood_data.get("moods", []),
                commercial_tags=commercial_tags,
                use_cases=mood_data.get("use_cases", []),
                sounds_like=mood_data.get("sounds_like", [])
            )
            db.add(track_tags_db)

        await db.commit()
        await db.refresh(track_tags_db)

        return {
            "moods": track_tags_db.moods,
            "commercial_tags": track_tags_db.commercial_tags,
            "use_cases": track_tags_db.use_cases,
            "sounds_like": track_tags_db.sounds_like,
        }
    except Exception as e:
        logger.error(f"Error generating tags for track {track_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate tags.")


@router.post("/{track_id}/generate-pitch")
async def generate_pitch(
    track_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Generate AI pitch copy for a track."""
    # Get track with analysis and tags
    result = await db.execute(
        select(Track, Analysis, TrackTags)
        .join(Analysis, Track.id == Analysis.track_id)
        .outerjoin(TrackTags, Track.id == TrackTags.track_id)
        .where(Track.id == track_id)
    )
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="Track or analysis not found")

    track, analysis, track_tags = row

    if not analysis.sonic_genome:
        raise HTTPException(status_code=400, detail="Sonic genome not available for this track.")

    # Get artist name
    artist_name = None
    if track.artist_id:
        result = await db.execute(select(Artist).where(Artist.id == track.artist_id))
        artist = result.scalar_one_or_none()
        if artist:
            artist_name = artist.name

    try:
        pitch_generator = PitchGenerator()
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))

    try:
        pitch_data = pitch_generator.generate_pitch(
            track_title=track.title,
            artist_name=artist_name or "Unknown Artist",
            sonic_genome=analysis.sonic_genome,
            lyrical_genome=analysis.lyrical_genome,
            tags={
                "moods": track_tags.moods,
                "commercial_tags": track_tags.commercial_tags,
                "sounds_like": track_tags.sounds_like,
            } if track_tags else None
        )

        result = await db.execute(select(PitchCopy).where(PitchCopy.track_id == track_id))
        pitch_copy_db = result.scalar_one_or_none()

        if pitch_copy_db:
            pitch_copy_db.elevator_pitch = pitch_data.get("elevator_pitch")
            pitch_copy_db.short_description = pitch_data.get("short_description")
            pitch_copy_db.sync_pitch = pitch_data.get("sync_pitch")
            pitch_copy_db.cost = pitch_data.get("cost")
            pitch_copy_db.generated_at = pitch_data.get("generated_at")
        else:
            pitch_copy_db = PitchCopy(
                track_id=track_id,
                elevator_pitch=pitch_data.get("elevator_pitch"),
                short_description=pitch_data.get("short_description"),
                sync_pitch=pitch_data.get("sync_pitch"),
                cost=pitch_data.get("cost"),
                generated_at=pitch_data.get("generated_at")
            )
            db.add(pitch_copy_db)

        await db.commit()
        await db.refresh(pitch_copy_db)

        return pitch_data
    except Exception as e:
        logger.error(f"Error generating pitch for track {track_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate pitch copy.")