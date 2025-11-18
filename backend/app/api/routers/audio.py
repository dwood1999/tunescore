"""Audio file serving endpoints."""

import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...models import Track, TrackAsset

logger = logging.getLogger(__name__)

router = APIRouter()

STORAGE_DIR = Path("files")


@router.get("/{track_id}/stream")
async def stream_audio(
    track_id: int,
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    """
    Stream audio file for a track.
    
    Returns the audio file with appropriate headers for streaming.
    """
    # Get track asset
    stmt = select(TrackAsset).where(TrackAsset.track_id == track_id)
    result = await db.execute(stmt)
    track_asset = result.scalar_one_or_none()
    
    if not track_asset or not track_asset.audio_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio file not found for this track",
        )
    
    audio_path = Path(track_asset.audio_path)
    
    if not audio_path.exists():
        logger.error(f"Audio file not found on disk: {audio_path}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio file not found on disk",
        )
    
    # Determine media type
    media_types = {
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "flac": "audio/flac",
        "m4a": "audio/mp4",
        "ogg": "audio/ogg",
    }
    
    media_type = media_types.get(
        track_asset.audio_format.lower() if track_asset.audio_format else "mp3",
        "audio/mpeg",
    )
    
    return FileResponse(
        path=audio_path,
        media_type=media_type,
        filename=f"track_{track_id}.{track_asset.audio_format}",
        headers={
            "Accept-Ranges": "bytes",
            "Cache-Control": "public, max-age=31536000",
        },
    )

