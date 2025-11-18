"""Search and RIYL (Recommended If You Like) endpoints."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...models import Analysis, Artist, Track
from ...services.embeddings.search import SimilaritySearch
from ...services.similarity.artist_similarity import calculate_artist_similarity

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/riyl/{track_id}", response_model=dict[str, Any])
async def get_riyl_recommendations(
    track_id: int,
    limit: int = Query(5, ge=1, le=20, description="Number of recommendations"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Get RIYL (Recommended If You Like) recommendations for a track.

    Returns tracks that are similar based on:
    - Title and artist
    - Lyrical themes
    - Lyrics content

    Uses vector embeddings and cosine similarity.
    """
    search = SimilaritySearch()

    try:
        results = await search.get_riyl_recommendations(
            track_id=track_id, db=db, limit=limit
        )

        if results["reference_track"] is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Track not found"
            )

        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RIYL search failed for track {track_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        )


@router.get("/similar/{track_id}", response_model=list[dict[str, Any]])
async def find_similar_tracks(
    track_id: int,
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
    min_similarity: float = Query(
        0.5, ge=0.0, le=1.0, description="Minimum similarity score"
    ),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """
    Find tracks similar to the given track.

    Returns a list of similar tracks with similarity scores.
    """
    search = SimilaritySearch()

    try:
        return await search.find_similar_tracks(
            track_id=track_id, db=db, limit=limit, min_similarity=min_similarity
        )

    except Exception as e:
        logger.error(f"Similarity search failed for track {track_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        )


@router.get("/query", response_model=list[dict[str, Any]])
async def search_by_text(
    q: str = Query(..., min_length=3, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
    min_similarity: float = Query(
        0.3, ge=0.0, le=1.0, description="Minimum similarity score"
    ),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """
    Search for tracks using a text query.

    Examples:
    - "sad love songs"
    - "upbeat party music"
    - "songs about heartbreak"

    Uses semantic search with embeddings.
    """
    search = SimilaritySearch()

    try:
        return await search.find_similar_by_text(
            query=q, db=db, limit=limit, min_similarity=min_similarity
        )

    except Exception as e:
        logger.error(f"Text search failed for query '{q}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        )


@router.get("/artists/compare/{artist1_id}/{artist2_id}", response_model=dict[str, Any])
async def compare_artists(
    artist1_id: int,
    artist2_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Compare two artists based on their sonic and lyrical fingerprints.
    
    Returns:
    - overall_similarity: 0-100 score
    - sonic_similarity: How similar their sound is
    - lyrical_similarity: How similar their lyrics are
    - style_match: Category (nearly_identical, very_similar, similar, somewhat_similar, different)
    - sonic_breakdown: Detailed feature comparison
    - lyrical_breakdown: Detailed lyrical comparison
    """
    try:
        # Get artist 1 tracks with analysis
        stmt1 = (
            select(Track, Analysis, Artist)
            .join(Analysis, Track.id == Analysis.track_id)
            .join(Artist, Track.artist_id == Artist.id)
            .where(Artist.id == artist1_id)
        )
        result1 = await db.execute(stmt1)
        rows1 = result1.all()
        
        # Get artist 2 tracks with analysis
        stmt2 = (
            select(Track, Analysis, Artist)
            .join(Analysis, Track.id == Analysis.track_id)
            .join(Artist, Track.artist_id == Artist.id)
            .where(Artist.id == artist2_id)
        )
        result2 = await db.execute(stmt2)
        rows2 = result2.all()
        
        if not rows1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artist {artist1_id} not found or has no analyzed tracks"
            )
        
        if not rows2:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artist {artist2_id} not found or has no analyzed tracks"
            )
        
        # Extract artist names
        artist1_name = rows1[0][2].name
        artist2_name = rows2[0][2].name
        
        # Prepare track data
        artist1_tracks = [
            {
                "sonic_genome": analysis.sonic_genome,
                "lyrical_genome": analysis.lyrical_genome,
            }
            for _, analysis, _ in rows1
        ]
        
        artist2_tracks = [
            {
                "sonic_genome": analysis.sonic_genome,
                "lyrical_genome": analysis.lyrical_genome,
            }
            for _, analysis, _ in rows2
        ]
        
        # Calculate similarity
        similarity = calculate_artist_similarity(artist1_tracks, artist2_tracks)
        
        # Add artist info
        similarity["artist1"] = {
            "id": artist1_id,
            "name": artist1_name,
            "track_count": len(artist1_tracks),
        }
        similarity["artist2"] = {
            "id": artist2_id,
            "name": artist2_name,
            "track_count": len(artist2_tracks),
        }
        
        logger.info(
            f"Compared artists {artist1_name} and {artist2_name}: "
            f"{similarity['overall_similarity']}% similar"
        )
        
        return similarity
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Artist comparison failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Comparison failed: {str(e)}",
        )
