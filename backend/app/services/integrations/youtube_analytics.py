"""YouTube Analytics API integration for viewing statistics and demographics.

Reference: https://developers.google.com/youtube/analytics
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ...core.config import settings

logger = logging.getLogger(__name__)


class YouTubeAnalyticsClient:
    """Client for YouTube Analytics API v2.
    
    Provides access to:
    - View statistics (views, watch time, average view duration)
    - Demographics (age, gender, geography)
    - Traffic sources (YouTube search, suggested videos, external)
    - Device types (mobile, desktop, TV)
    - Engagement metrics (likes, shares, comments, subscribers)
    - Top videos and playlists
    - Revenue data (for monetized channels)
    """

    def __init__(self):
        """Initialize YouTube Analytics client."""
        self._client: Any | None = None

    @property
    def client(self) -> Any:
        """Get YouTube Analytics API client.
        
        Lazy loads the client on first access.
        Requires OAuth 2.0 credentials for channel owners/content owners.
        """
        if self._client is None:
            # TODO: Implement OAuth 2.0 flow for user authentication
            # For now, using API key (limited to public data)
            if not settings.YOUTUBE_API_KEY:
                raise ValueError("YouTube API key not configured")

            # Note: Full Analytics API requires OAuth, not just API key
            # This is a placeholder - will need OAuth implementation
            self._client = build(
                "youtubeAnalytics", 
                "v2", 
                developerKey=settings.YOUTUBE_API_KEY
            )
            logger.info("YouTube Analytics client initialized")

        return self._client

    def get_channel_statistics(
        self,
        channel_id: str,
        start_date: str | None = None,
        end_date: str | None = None,
        metrics: list[str] | None = None,
    ) -> dict[str, Any]:
        """Get channel-level statistics.
        
        Args:
            channel_id: YouTube channel ID
            start_date: Start date (YYYY-MM-DD). Defaults to 30 days ago
            end_date: End date (YYYY-MM-DD). Defaults to today
            metrics: List of metrics to retrieve. Defaults to core metrics:
                    - views: Total views
                    - estimatedMinutesWatched: Watch time in minutes
                    - averageViewDuration: Average view duration (seconds)
                    - subscribersGained: New subscribers
                    - subscribersLost: Lost subscribers
                    - likes: Total likes
                    - shares: Total shares
                    - comments: Total comments
        
        Returns:
            Dictionary containing:
                - rows: List of metric data rows
                - columnHeaders: Metric names and types
                - kind: "youtubeAnalytics#resultTable"
        
        Example:
            {
                "rows": [[12500, 8750, 42, 15, 3, 450, 89, 234]],
                "columnHeaders": [
                    {"name": "views", "dataType": "INTEGER"},
                    {"name": "estimatedMinutesWatched", "dataType": "INTEGER"},
                    ...
                ]
            }
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not metrics:
            metrics = [
                "views",
                "estimatedMinutesWatched",
                "averageViewDuration",
                "subscribersGained",
                "subscribersLost",
                "likes",
                "shares",
                "comments",
            ]

        try:
            request = self.client.reports().query(
                ids=f"channel=={channel_id}",
                startDate=start_date,
                endDate=end_date,
                metrics=",".join(metrics),
            )
            response = request.execute()
            
            logger.info(f"Retrieved analytics for channel {channel_id}: {response.get('rows', [[]])[0] if response.get('rows') else 'no data'}")
            return response

        except HttpError as e:
            logger.error(f"YouTube Analytics API error for channel {channel_id}: {e}")
            raise

    def get_video_statistics(
        self,
        video_id: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """Get video-level statistics.
        
        Args:
            video_id: YouTube video ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            Video analytics data including views, watch time, engagement
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        try:
            request = self.client.reports().query(
                ids="channel==MINE",  # Requires OAuth for user's channel
                startDate=start_date,
                endDate=end_date,
                metrics="views,estimatedMinutesWatched,averageViewDuration,likes,shares,comments",
                dimensions="video",
                filters=f"video=={video_id}",
            )
            response = request.execute()
            return response

        except HttpError as e:
            logger.error(f"YouTube Analytics API error for video {video_id}: {e}")
            raise

    def get_demographics(
        self,
        channel_id: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """Get audience demographics (age and gender).
        
        Args:
            channel_id: YouTube channel ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            Demographic breakdown:
                - ageGroup: age13-17, age18-24, age25-34, age35-44, age45-54, age55-64, age65-
                - gender: male, female
                - viewsPercentage: Percentage of views for each demographic
        
        Example:
            {
                "rows": [
                    ["age18-24", "female", 23.5],
                    ["age18-24", "male", 18.2],
                    ["age25-34", "female", 15.8],
                    ...
                ]
            }
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        try:
            request = self.client.reports().query(
                ids=f"channel=={channel_id}",
                startDate=start_date,
                endDate=end_date,
                metrics="viewsPercentage",
                dimensions="ageGroup,gender",
            )
            response = request.execute()
            return response

        except HttpError as e:
            logger.error(f"YouTube Analytics API error for demographics {channel_id}: {e}")
            raise

    def get_traffic_sources(
        self,
        channel_id: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """Get traffic source breakdown.
        
        Args:
            channel_id: YouTube channel ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            Traffic sources:
                - insightTrafficSourceType: ADVERTISING, ANNOTATION, CAMPAIGN_CARD,
                  END_SCREEN, EXT_URL, HASHTAGS, NOTIFICATION, PLAYLIST,
                  PROMOTED, RELATED_VIDEO, SHORTS, SUBSCRIBER, YT_CHANNEL,
                  YT_OTHER_PAGE, YT_SEARCH, etc.
                - views: Views from each source
        
        Example:
            {
                "rows": [
                    ["YT_SEARCH", 45000],
                    ["RELATED_VIDEO", 32000],
                    ["EXTERNAL", 15000],
                    ...
                ]
            }
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        try:
            request = self.client.reports().query(
                ids=f"channel=={channel_id}",
                startDate=start_date,
                endDate=end_date,
                metrics="views",
                dimensions="insightTrafficSourceType",
                sort="-views",
            )
            response = request.execute()
            return response

        except HttpError as e:
            logger.error(f"YouTube Analytics API error for traffic sources {channel_id}: {e}")
            raise

    def get_device_types(
        self,
        channel_id: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """Get device type breakdown.
        
        Args:
            channel_id: YouTube channel ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            Device types:
                - deviceType: DESKTOP, MOBILE, TABLET, TV, GAME_CONSOLE, UNKNOWN_PLATFORM
                - views: Views from each device type
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        try:
            request = self.client.reports().query(
                ids=f"channel=={channel_id}",
                startDate=start_date,
                endDate=end_date,
                metrics="views",
                dimensions="deviceType",
                sort="-views",
            )
            response = request.execute()
            return response

        except HttpError as e:
            logger.error(f"YouTube Analytics API error for device types {channel_id}: {e}")
            raise

    def get_geography(
        self,
        channel_id: str,
        start_date: str | None = None,
        end_date: str | None = None,
        max_results: int = 25,
    ) -> dict[str, Any]:
        """Get geographic breakdown (by country).
        
        Args:
            channel_id: YouTube channel ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            max_results: Maximum number of countries to return
        
        Returns:
            Geographic data:
                - country: ISO 3166-1 alpha-2 country code
                - views: Views from each country
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        try:
            request = self.client.reports().query(
                ids=f"channel=={channel_id}",
                startDate=start_date,
                endDate=end_date,
                metrics="views",
                dimensions="country",
                sort="-views",
                maxResults=max_results,
            )
            response = request.execute()
            return response

        except HttpError as e:
            logger.error(f"YouTube Analytics API error for geography {channel_id}: {e}")
            raise

    def get_top_videos(
        self,
        channel_id: str,
        start_date: str | None = None,
        end_date: str | None = None,
        max_results: int = 10,
    ) -> dict[str, Any]:
        """Get top-performing videos.
        
        Args:
            channel_id: YouTube channel ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            max_results: Maximum number of videos to return
        
        Returns:
            Top videos sorted by views
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        try:
            request = self.client.reports().query(
                ids=f"channel=={channel_id}",
                startDate=start_date,
                endDate=end_date,
                metrics="views,estimatedMinutesWatched,likes,shares,comments",
                dimensions="video",
                sort="-views",
                maxResults=max_results,
            )
            response = request.execute()
            return response

        except HttpError as e:
            logger.error(f"YouTube Analytics API error for top videos {channel_id}: {e}")
            raise


# Global instance
_youtube_analytics_client: YouTubeAnalyticsClient | None = None


def get_youtube_analytics_client() -> YouTubeAnalyticsClient:
    """Get the global YouTube Analytics client instance."""
    global _youtube_analytics_client
    if _youtube_analytics_client is None:
        _youtube_analytics_client = YouTubeAnalyticsClient()
    return _youtube_analytics_client

