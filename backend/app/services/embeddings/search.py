"""Vector similarity search for RIYL (Recommended If You Like)."""

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models import Artist, Embedding, Track
from .generator import cosine_similarity, get_embedding_generator

logger = logging.getLogger(__name__)


class SimilaritySearch:
    """Search for similar tracks using vector embeddings."""

    def __init__(self):
        """Initialize similarity search."""
        self.generator = get_embedding_generator()

    async def find_similar_tracks(
        self,
        track_id: int,
        db: AsyncSession,
        limit: int = 10,
        min_similarity: float = 0.5,
    ) -> list[dict[str, Any]]:
        """
        Find tracks similar to the given track.

        Args:
            track_id: ID of the reference track
            db: Database session
            limit: Maximum number of results
            min_similarity: Minimum similarity threshold (0-1)

        Returns:
            List of similar tracks with similarity scores
        """
        # Get the reference track's embedding
        stmt = select(Embedding).where(Embedding.track_id == track_id)
        result = await db.execute(stmt)
        ref_embedding_obj = result.scalar_one_or_none()

        if not ref_embedding_obj:
            logger.warning(f"No embedding found for track {track_id}")
            return []

        ref_vector = ref_embedding_obj.vector

        # Get all other embeddings
        stmt = select(Embedding).where(Embedding.track_id != track_id)
        result = await db.execute(stmt)
        all_embeddings = result.scalars().all()

        # Compute similarities
        similarities: list[tuple[int, float]] = []
        for emb in all_embeddings:
            similarity = cosine_similarity(ref_vector, emb.vector)
            if similarity >= min_similarity:
                similarities.append((emb.track_id, similarity))

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Limit results
        similarities = similarities[:limit]

        # Fetch track details
        track_ids = [tid for tid, _ in similarities]
        if not track_ids:
            return []

        stmt = (
            select(Track, Artist)
            .outerjoin(Artist, Track.artist_id == Artist.id)
            .where(Track.id.in_(track_ids))
        )
        result = await db.execute(stmt)
        tracks_data = {track.id: (track, artist) for track, artist in result.all()}

        # Build results
        results = []
        for track_id, similarity in similarities:
            if track_id in tracks_data:
                track, artist = tracks_data[track_id]
                results.append(
                    {
                        "track_id": track.id,
                        "title": track.title,
                        "artist_name": artist.name if artist else None,
                        "similarity_score": round(similarity, 3),
                        "spotify_id": track.spotify_id,
                    }
                )

        return results

    async def find_similar_by_text(
        self,
        query: str,
        db: AsyncSession,
        limit: int = 10,
        min_similarity: float = 0.3,
    ) -> list[dict[str, Any]]:
        """
        Find tracks similar to a text query.

        Useful for "find me songs like X" queries.

        Args:
            query: Text description or query
            db: Database session
            limit: Maximum number of results
            min_similarity: Minimum similarity threshold

        Returns:
            List of matching tracks with similarity scores
        """
        # Generate embedding for query
        query_vector = self.generator.generate_embedding(query)

        # Get all embeddings
        stmt = select(Embedding)
        result = await db.execute(stmt)
        all_embeddings = result.scalars().all()

        # Compute similarities
        similarities: list[tuple[int, float]] = []
        for emb in all_embeddings:
            similarity = cosine_similarity(query_vector, emb.vector)
            if similarity >= min_similarity:
                similarities.append((emb.track_id, similarity))

        # Sort and limit
        similarities.sort(key=lambda x: x[1], reverse=True)
        similarities = similarities[:limit]

        # Fetch track details
        track_ids = [tid for tid, _ in similarities]
        if not track_ids:
            return []

        stmt = (
            select(Track, Artist)
            .outerjoin(Artist, Track.artist_id == Artist.id)
            .where(Track.id.in_(track_ids))
        )
        result = await db.execute(stmt)
        tracks_data = {track.id: (track, artist) for track, artist in result.all()}

        # Build results
        results = []
        for track_id, similarity in similarities:
            if track_id in tracks_data:
                track, artist = tracks_data[track_id]
                results.append(
                    {
                        "track_id": track.id,
                        "title": track.title,
                        "artist_name": artist.name if artist else None,
                        "similarity_score": round(similarity, 3),
                        "spotify_id": track.spotify_id,
                    }
                )

        return results

    async def get_riyl_recommendations(
        self,
        track_id: int,
        db: AsyncSession,
        limit: int = 5,
    ) -> dict[str, Any]:
        """
        Get RIYL (Recommended If You Like) recommendations for a track.

        This is the main user-facing RIYL feature.

        Args:
            track_id: ID of the reference track
            db: Database session
            limit: Number of recommendations

        Returns:
            Dictionary with recommendations and metadata
        """
        # Get reference track
        stmt = (
            select(Track, Artist)
            .outerjoin(Artist, Track.artist_id == Artist.id)
            .where(Track.id == track_id)
        )
        result = await db.execute(stmt)
        track_data = result.one_or_none()

        if not track_data:
            return {
                "reference_track": None,
                "recommendations": [],
                "message": "Track not found",
            }

        track, artist = track_data

        # Find similar tracks
        similar_tracks = await self.find_similar_tracks(
            track_id=track_id, db=db, limit=limit, min_similarity=0.5
        )

        return {
            "reference_track": {
                "id": track.id,
                "title": track.title,
                "artist_name": artist.name if artist else None,
            },
            "recommendations": similar_tracks,
            "count": len(similar_tracks),
            "message": f"Found {len(similar_tracks)} similar tracks",
        }


async def create_embedding_for_track(
    track_id: int,
    db: AsyncSession,
) -> Embedding | None:
    """
    Create or update embedding for a track.

    Args:
        track_id: ID of the track
        db: Database session

    Returns:
        Embedding object or None if failed
    """
    # Get track with related data
    stmt = (
        select(Track, Artist)
        .outerjoin(Artist, Track.artist_id == Artist.id)
        .where(Track.id == track_id)
    )
    result = await db.execute(stmt)
    track_data = result.one_or_none()

    if not track_data:
        logger.error(f"Track {track_id} not found")
        return None

    track, artist = track_data

    # Get track asset for lyrics
    from ...models import TrackAsset

    stmt = select(TrackAsset).where(TrackAsset.track_id == track_id)
    result = await db.execute(stmt)
    track_asset = result.scalar_one_or_none()

    # Get analysis for themes
    from ...models import Analysis

    stmt = (
        select(Analysis)
        .where(Analysis.track_id == track_id)
        .order_by(Analysis.created_at.desc())
    )
    result = await db.execute(stmt)
    analysis = result.scalar_one_or_none()

    # Extract themes from lyrical genome
    themes = None
    if analysis and analysis.lyrical_genome:
        themes = analysis.lyrical_genome.get("themes", [])

    # Generate embedding
    generator = get_embedding_generator()
    try:
        vector = generator.generate_track_embedding(
            title=track.title,
            lyrics=track_asset.lyrics_text if track_asset else None,
            themes=themes,
            artist_name=artist.name if artist else None,
        )
    except Exception as e:
        logger.error(f"Failed to generate embedding for track {track_id}: {e}")
        return None

    # Check if embedding already exists
    stmt = select(Embedding).where(Embedding.track_id == track_id)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        # Update existing
        existing.vector = vector
        existing.model_version = generator.model_name
        embedding = existing
    else:
        # Create new
        embedding = Embedding(
            track_id=track_id,
            vector=vector,
            model_version=generator.model_name,
        )
        db.add(embedding)

    await db.flush()
    return embedding
