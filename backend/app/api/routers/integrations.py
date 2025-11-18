"""External platform integrations (Spotify, YouTube, etc.)."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status

from ...services.integrations.spotify import get_spotify_client
from ...services.integrations.youtube import get_youtube_client
from ...services.integrations.youtube_analytics import get_youtube_analytics_client

logger = logging.getLogger(__name__)

router = APIRouter()


# Spotify endpoints
@router.get("/spotify/auth-url", response_model=dict[str, str])
async def get_spotify_auth_url() -> dict[str, str]:
    """
    Get Spotify OAuth authorization URL.

    User should visit this URL to authorize the application.
    """
    try:
        spotify = get_spotify_client()
        auth_url = spotify.get_auth_url()

        return {
            "auth_url": auth_url,
            "message": "Visit this URL to authorize Spotify access",
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Spotify not configured: {str(e)}",
        )


@router.get("/spotify/callback")
async def spotify_callback(
    code: str = Query(..., description="Authorization code from Spotify"),
) -> dict[str, Any]:
    """
    Handle Spotify OAuth callback.

    Exchange authorization code for access token.
    """
    try:
        spotify = get_spotify_client()
        token_info = spotify.get_access_token(code)

        return {
            "access_token": token_info.get("access_token"),
            "refresh_token": token_info.get("refresh_token"),
            "expires_in": token_info.get("expires_in"),
            "message": "Successfully authenticated with Spotify",
        }
    except Exception as e:
        logger.error(f"Spotify callback failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Authentication failed: {str(e)}",
        )


@router.get("/spotify/track/{track_id}", response_model=dict[str, Any])
async def get_spotify_track(track_id: str) -> dict[str, Any]:
    """
    Get track information from Spotify.

    Args:
        track_id: Spotify track ID
    """
    try:
        spotify = get_spotify_client()
        return spotify.get_track(track_id)

    except Exception as e:
        logger.error(f"Failed to fetch Spotify track {track_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Track not found: {str(e)}"
        )


@router.get("/spotify/track/{track_id}/audio-features", response_model=dict[str, Any])
async def get_spotify_audio_features(track_id: str) -> dict[str, Any]:
    """
    Get audio features for a Spotify track.

    Returns pre-computed features like danceability, energy, valence, etc.
    """
    try:
        spotify = get_spotify_client()
        features = spotify.get_audio_features(track_id)

        if not features:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Audio features not found"
            )

        return features
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch audio features for {track_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch audio features: {str(e)}",
        )


@router.get("/spotify/artist/{artist_id}", response_model=dict[str, Any])
async def get_spotify_artist(artist_id: str) -> dict[str, Any]:
    """
    Get artist information from Spotify.
    """
    try:
        spotify = get_spotify_client()
        return spotify.get_artist(artist_id)

    except Exception as e:
        logger.error(f"Failed to fetch Spotify artist {artist_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Artist not found: {str(e)}"
        )


@router.get("/spotify/artist/{artist_id}/stats", response_model=dict[str, Any])
async def get_spotify_artist_stats(artist_id: str) -> dict[str, Any]:
    """
    Get artist statistics from Spotify.

    Returns followers, popularity, genres, etc.
    """
    try:
        spotify = get_spotify_client()
        return spotify.get_artist_stats(artist_id)

    except Exception as e:
        logger.error(f"Failed to fetch artist stats for {artist_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch artist stats: {str(e)}",
        )


@router.get("/spotify/artist/{artist_id}/related", response_model=list[dict[str, Any]])
async def get_related_artists(artist_id: str) -> list[dict[str, Any]]:
    """
    Get artists related to the given artist.

    Useful for RIYL (Recommended If You Like) feature.
    """
    try:
        spotify = get_spotify_client()
        return spotify.get_related_artists(artist_id)

    except Exception as e:
        logger.error(f"Failed to fetch related artists for {artist_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch related artists: {str(e)}",
        )


@router.get("/spotify/search/track", response_model=list[dict[str, Any]])
async def search_spotify_tracks(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
) -> list[dict[str, Any]]:
    """
    Search for tracks on Spotify.
    """
    try:
        spotify = get_spotify_client()
        return spotify.search_track(q, limit=limit)

    except Exception as e:
        logger.error(f"Spotify track search failed for '{q}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        )


@router.get("/spotify/search/artist", response_model=list[dict[str, Any]])
async def search_spotify_artists(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
) -> list[dict[str, Any]]:
    """
    Search for artists on Spotify.
    """
    try:
        spotify = get_spotify_client()
        return spotify.search_artist(q, limit=limit)

    except Exception as e:
        logger.error(f"Spotify artist search failed for '{q}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        )


# YouTube endpoints
@router.get("/youtube/video/{video_id}", response_model=dict[str, Any])
async def get_youtube_video(video_id: str) -> dict[str, Any]:
    """
    Get video information from YouTube.

    Args:
        video_id: YouTube video ID
    """
    try:
        youtube = get_youtube_client()
        return youtube.get_video(video_id)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to fetch YouTube video {video_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch video: {str(e)}",
        )


@router.get("/youtube/video/{video_id}/stats", response_model=dict[str, Any])
async def get_youtube_video_stats(video_id: str) -> dict[str, Any]:
    """
    Get video statistics from YouTube.

    Returns view count, like count, comment count, etc.
    """
    try:
        youtube = get_youtube_client()
        return youtube.get_video_stats(video_id)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to fetch YouTube video stats for {video_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch video stats: {str(e)}",
        )


@router.get("/youtube/channel/{channel_id}", response_model=dict[str, Any])
async def get_youtube_channel(channel_id: str) -> dict[str, Any]:
    """
    Get channel information from YouTube.
    """
    try:
        youtube = get_youtube_client()
        return youtube.get_channel(channel_id)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to fetch YouTube channel {channel_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch channel: {str(e)}",
        )


@router.get("/youtube/channel/{channel_id}/stats", response_model=dict[str, Any])
async def get_youtube_channel_stats(channel_id: str) -> dict[str, Any]:
    """
    Get channel statistics from YouTube.

    Returns subscriber count, view count, video count.
    """
    try:
        youtube = get_youtube_client()
        return youtube.get_channel_stats(channel_id)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to fetch YouTube channel stats for {channel_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch channel stats: {str(e)}",
        )


@router.get("/youtube/search/video", response_model=list[dict[str, Any]])
async def search_youtube_videos(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
    order: str = Query("relevance", description="Sort order"),
) -> list[dict[str, Any]]:
    """
    Search for videos on YouTube.

    Order options: date, rating, relevance, title, videoCount, viewCount
    """
    try:
        youtube = get_youtube_client()
        return youtube.search_videos(q, max_results=limit, order=order)

    except Exception as e:
        logger.error(f"YouTube video search failed for '{q}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        )


@router.get("/youtube/search/channel", response_model=list[dict[str, Any]])
async def search_youtube_channels(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
) -> list[dict[str, Any]]:
    """
    Search for channels on YouTube.
    """
    try:
        youtube = get_youtube_client()
        return youtube.search_channels(q, max_results=limit)

    except Exception as e:
        logger.error(f"YouTube channel search failed for '{q}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        )


@router.get("/youtube/trending/music", response_model=list[dict[str, Any]])
async def get_trending_music(
    region: str = Query("US", description="ISO 3166-1 alpha-2 country code"),
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
) -> list[dict[str, Any]]:
    """
    Get trending music videos on YouTube.
    """
    try:
        youtube = get_youtube_client()
        return youtube.get_trending_music_videos(region_code=region, max_results=limit)

    except Exception as e:
        logger.error(f"Failed to fetch trending music videos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch trending videos: {str(e)}",
        )


# YouTube Analytics endpoints
@router.get("/youtube-analytics/channel/{channel_id}/stats", response_model=dict[str, Any])
async def get_youtube_channel_analytics(
    channel_id: str,
    start_date: str | None = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: str | None = Query(None, description="End date (YYYY-MM-DD)"),
) -> dict[str, Any]:
    """
    Get YouTube Analytics statistics for a channel.
    
    Returns views, watch time, subscriber changes, engagement metrics.
    Requires YouTube Analytics API to be enabled.
    """
    try:
        analytics = get_youtube_analytics_client()
        return analytics.get_channel_statistics(
            channel_id=channel_id,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        logger.error(f"YouTube Analytics failed for channel {channel_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analytics request failed: {str(e)}",
        )


@router.get("/youtube-analytics/channel/{channel_id}/demographics", response_model=dict[str, Any])
async def get_youtube_channel_demographics(
    channel_id: str,
    start_date: str | None = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: str | None = Query(None, description="End date (YYYY-MM-DD)"),
) -> dict[str, Any]:
    """
    Get audience demographics (age and gender) for a YouTube channel.
    
    Returns breakdown by age group (13-17, 18-24, 25-34, etc.) and gender.
    """
    try:
        analytics = get_youtube_analytics_client()
        return analytics.get_demographics(
            channel_id=channel_id,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        logger.error(f"YouTube demographics failed for channel {channel_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Demographics request failed: {str(e)}",
        )


@router.get("/youtube-analytics/channel/{channel_id}/traffic-sources", response_model=dict[str, Any])
async def get_youtube_traffic_sources(
    channel_id: str,
    start_date: str | None = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: str | None = Query(None, description="End date (YYYY-MM-DD)"),
) -> dict[str, Any]:
    """
    Get traffic source breakdown for a YouTube channel.
    
    Shows where views are coming from (YouTube search, suggested videos, external links, etc.)
    """
    try:
        analytics = get_youtube_analytics_client()
        return analytics.get_traffic_sources(
            channel_id=channel_id,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        logger.error(f"YouTube traffic sources failed for channel {channel_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Traffic sources request failed: {str(e)}",
        )


@router.get("/youtube-analytics/channel/{channel_id}/geography", response_model=dict[str, Any])
async def get_youtube_geography(
    channel_id: str,
    start_date: str | None = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: str | None = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(25, ge=1, le=100, description="Number of countries"),
) -> dict[str, Any]:
    """
    Get geographic breakdown for a YouTube channel (by country).
    
    Shows top countries where your content is viewed.
    """
    try:
        analytics = get_youtube_analytics_client()
        return analytics.get_geography(
            channel_id=channel_id,
            start_date=start_date,
            end_date=end_date,
            max_results=limit
        )
    except Exception as e:
        logger.error(f"YouTube geography failed for channel {channel_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Geography request failed: {str(e)}",
        )


@router.get("/youtube-analytics/channel/{channel_id}/top-videos", response_model=dict[str, Any])
async def get_youtube_top_videos(
    channel_id: str,
    start_date: str | None = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: str | None = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(10, ge=1, le=50, description="Number of videos"),
) -> dict[str, Any]:
    """
    Get top-performing videos for a YouTube channel.
    
    Returns videos sorted by views with engagement metrics.
    """
    try:
        analytics = get_youtube_analytics_client()
        return analytics.get_top_videos(
            channel_id=channel_id,
            start_date=start_date,
            end_date=end_date,
            max_results=limit
        )
    except Exception as e:
        logger.error(f"YouTube top videos failed for channel {channel_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Top videos request failed: {str(e)}",
        )
