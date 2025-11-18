"""YouTube Data API integration."""

import logging
from typing import Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ...core.config import settings

logger = logging.getLogger(__name__)


class YouTubeClient:
    """Client for YouTube Data API v3."""

    def __init__(self):
        """Initialize YouTube client."""
        self._client: Any | None = None

    @property
    def client(self) -> Any:
        """
        Get YouTube API client.

        Lazy loads the client on first access.
        """
        if self._client is None:
            if not settings.YOUTUBE_API_KEY:
                raise ValueError("YouTube API key not configured")

            self._client = build("youtube", "v3", developerKey=settings.YOUTUBE_API_KEY)
            logger.info("YouTube client initialized")

        return self._client

    def get_video(self, video_id: str) -> dict[str, Any]:
        """
        Get video information.

        Args:
            video_id: YouTube video ID

        Returns:
            Video information dictionary
        """
        try:
            request = self.client.videos().list(
                part="snippet,statistics,contentDetails", id=video_id
            )
            response = request.execute()

            if not response.get("items"):
                raise ValueError(f"Video {video_id} not found")

            return response["items"][0]

        except HttpError as e:
            logger.error(f"YouTube API error fetching video {video_id}: {e}")
            raise

    def get_video_stats(self, video_id: str) -> dict[str, Any]:
        """
        Get video statistics (views, likes, comments).

        Args:
            video_id: YouTube video ID

        Returns:
            Dictionary with video stats
        """
        video = self.get_video(video_id)
        stats = video.get("statistics", {})

        return {
            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)),
            "comment_count": int(stats.get("commentCount", 0)),
            "favorite_count": int(stats.get("favoriteCount", 0)),
        }

    def get_channel(self, channel_id: str) -> dict[str, Any]:
        """
        Get channel information.

        Args:
            channel_id: YouTube channel ID

        Returns:
            Channel information dictionary
        """
        try:
            request = self.client.channels().list(
                part="snippet,statistics,contentDetails", id=channel_id
            )
            response = request.execute()

            if not response.get("items"):
                raise ValueError(f"Channel {channel_id} not found")

            return response["items"][0]

        except HttpError as e:
            logger.error(f"YouTube API error fetching channel {channel_id}: {e}")
            raise

    def get_channel_stats(self, channel_id: str) -> dict[str, Any]:
        """
        Get channel statistics (subscribers, views, video count).

        Args:
            channel_id: YouTube channel ID

        Returns:
            Dictionary with channel stats
        """
        channel = self.get_channel(channel_id)
        stats = channel.get("statistics", {})

        return {
            "subscriber_count": int(stats.get("subscriberCount", 0)),
            "view_count": int(stats.get("viewCount", 0)),
            "video_count": int(stats.get("videoCount", 0)),
        }

    def search_videos(
        self,
        query: str,
        max_results: int = 10,
        order: str = "relevance",
    ) -> list[dict[str, Any]]:
        """
        Search for videos.

        Args:
            query: Search query
            max_results: Maximum number of results (1-50)
            order: Sort order (date, rating, relevance, title, videoCount, viewCount)

        Returns:
            List of video results
        """
        try:
            request = self.client.search().list(
                part="snippet",
                q=query,
                type="video",
                maxResults=min(max_results, 50),
                order=order,
            )
            response = request.execute()

            return response.get("items", [])

        except HttpError as e:
            logger.error(f"YouTube API error searching for '{query}': {e}")
            raise

    def search_channels(
        self,
        query: str,
        max_results: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Search for channels.

        Args:
            query: Search query
            max_results: Maximum number of results (1-50)

        Returns:
            List of channel results
        """
        try:
            request = self.client.search().list(
                part="snippet", q=query, type="channel", maxResults=min(max_results, 50)
            )
            response = request.execute()

            return response.get("items", [])

        except HttpError as e:
            logger.error(f"YouTube API error searching channels for '{query}': {e}")
            raise

    def get_channel_videos(
        self,
        channel_id: str,
        max_results: int = 10,
        order: str = "date",
    ) -> list[dict[str, Any]]:
        """
        Get videos from a channel.

        Args:
            channel_id: YouTube channel ID
            max_results: Maximum number of results (1-50)
            order: Sort order (date, rating, relevance, title, videoCount, viewCount)

        Returns:
            List of videos
        """
        try:
            request = self.client.search().list(
                part="snippet",
                channelId=channel_id,
                type="video",
                maxResults=min(max_results, 50),
                order=order,
            )
            response = request.execute()

            return response.get("items", [])

        except HttpError as e:
            logger.error(
                f"YouTube API error fetching videos for channel {channel_id}: {e}"
            )
            raise

    def get_trending_music_videos(
        self,
        region_code: str = "US",
        max_results: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Get trending music videos.

        Args:
            region_code: ISO 3166-1 alpha-2 country code
            max_results: Maximum number of results (1-50)

        Returns:
            List of trending music videos
        """
        try:
            request = self.client.videos().list(
                part="snippet,statistics",
                chart="mostPopular",
                regionCode=region_code,
                videoCategoryId="10",  # Music category
                maxResults=min(max_results, 50),
            )
            response = request.execute()

            return response.get("items", [])

        except HttpError as e:
            logger.error(f"YouTube API error fetching trending music videos: {e}")
            raise


# Global instance
_youtube_client: YouTubeClient | None = None


def get_youtube_client() -> YouTubeClient:
    """Get the global YouTube client instance."""
    global _youtube_client
    if _youtube_client is None:
        _youtube_client = YouTubeClient()
    return _youtube_client
