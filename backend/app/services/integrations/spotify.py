"""Spotify API integration using spotipy."""

import logging
from typing import Any

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

from ...core.config import settings

logger = logging.getLogger(__name__)


class SpotifyClient:
    """Client for Spotify Web API."""

    def __init__(self):
        """Initialize Spotify client."""
        self._client: spotipy.Spotify | None = None
        self._auth_client: spotipy.Spotify | None = None

    @property
    def client(self) -> spotipy.Spotify:
        """
        Get client with client credentials (for public data).

        Lazy loads the client on first access.
        """
        if self._client is None:
            if not settings.SPOTIFY_CLIENT_ID or not settings.SPOTIFY_CLIENT_SECRET:
                raise ValueError("Spotify credentials not configured")

            auth_manager = SpotifyClientCredentials(
                client_id=settings.SPOTIFY_CLIENT_ID,
                client_secret=settings.SPOTIFY_CLIENT_SECRET,
            )
            self._client = spotipy.Spotify(auth_manager=auth_manager)
            logger.info("Spotify client initialized with client credentials")

        return self._client

    def get_auth_client(self, access_token: str) -> spotipy.Spotify:
        """
        Get client with user access token (for user-specific data).

        Args:
            access_token: User's Spotify access token

        Returns:
            Authenticated Spotify client
        """
        return spotipy.Spotify(auth=access_token)

    def get_auth_url(self, redirect_uri: str | None = None) -> str:
        """
        Get Spotify OAuth authorization URL.

        Args:
            redirect_uri: OAuth redirect URI

        Returns:
            Authorization URL for user to visit
        """
        if not settings.SPOTIFY_CLIENT_ID or not settings.SPOTIFY_CLIENT_SECRET:
            raise ValueError("Spotify credentials not configured")

        redirect_uri = redirect_uri or settings.SPOTIFY_REDIRECT_URI

        sp_oauth = SpotifyOAuth(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET,
            redirect_uri=redirect_uri,
            scope="user-library-read user-top-read user-read-recently-played",
        )

        return sp_oauth.get_authorize_url()

    def get_access_token(
        self, code: str, redirect_uri: str | None = None
    ) -> dict[str, Any]:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from OAuth callback
            redirect_uri: OAuth redirect URI

        Returns:
            Token info dictionary
        """
        if not settings.SPOTIFY_CLIENT_ID or not settings.SPOTIFY_CLIENT_SECRET:
            raise ValueError("Spotify credentials not configured")

        redirect_uri = redirect_uri or settings.SPOTIFY_REDIRECT_URI

        sp_oauth = SpotifyOAuth(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET,
            redirect_uri=redirect_uri,
            scope="user-library-read user-top-read user-read-recently-played",
        )

        return sp_oauth.get_access_token(code)

    def get_track(self, track_id: str) -> dict[str, Any]:
        """
        Get track information from Spotify.

        Args:
            track_id: Spotify track ID

        Returns:
            Track information dictionary
        """
        return self.client.track(track_id)

    def get_audio_features(self, track_id: str) -> dict[str, Any]:
        """
        Get audio features for a track.

        Returns Spotify's pre-computed audio features:
        - danceability, energy, key, loudness, mode, speechiness
        - acousticness, instrumentalness, liveness, valence, tempo

        Args:
            track_id: Spotify track ID

        Returns:
            Audio features dictionary
        """
        features = self.client.audio_features([track_id])
        return features[0] if features else {}

    def get_artist(self, artist_id: str) -> dict[str, Any]:
        """
        Get artist information from Spotify.

        Args:
            artist_id: Spotify artist ID

        Returns:
            Artist information dictionary
        """
        return self.client.artist(artist_id)

    def get_artist_top_tracks(
        self, artist_id: str, country: str = "US"
    ) -> list[dict[str, Any]]:
        """
        Get artist's top tracks.

        Args:
            artist_id: Spotify artist ID
            country: Country code (ISO 3166-1 alpha-2)

        Returns:
            List of top tracks
        """
        results = self.client.artist_top_tracks(artist_id, country=country)
        return results.get("tracks", [])

    def get_related_artists(self, artist_id: str) -> list[dict[str, Any]]:
        """
        Get artists related to the given artist.

        Useful for RIYL (Recommended If You Like) feature.

        Args:
            artist_id: Spotify artist ID

        Returns:
            List of related artists
        """
        results = self.client.artist_related_artists(artist_id)
        return results.get("artists", [])

    def search_track(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """
        Search for tracks.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of track results
        """
        results = self.client.search(q=query, type="track", limit=limit)
        return results.get("tracks", {}).get("items", [])

    def search_artist(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """
        Search for artists.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of artist results
        """
        results = self.client.search(q=query, type="artist", limit=limit)
        return results.get("artists", {}).get("items", [])

    def get_artist_stats(self, artist_id: str) -> dict[str, Any]:
        """
        Get artist statistics (followers, popularity, etc.).

        Args:
            artist_id: Spotify artist ID

        Returns:
            Dictionary with artist stats
        """
        artist = self.get_artist(artist_id)

        return {
            "followers": artist.get("followers", {}).get("total", 0),
            "popularity": artist.get("popularity", 0),
            "genres": artist.get("genres", []),
            "external_urls": artist.get("external_urls", {}),
        }

    def get_user_top_tracks(
        self, access_token: str, time_range: str = "medium_term", limit: int = 20
    ) -> list[dict[str, Any]]:
        """
        Get user's top tracks (requires user authentication).

        Args:
            access_token: User's Spotify access token
            time_range: Time range (short_term, medium_term, long_term)
            limit: Maximum number of results

        Returns:
            List of user's top tracks
        """
        client = self.get_auth_client(access_token)
        results = client.current_user_top_tracks(time_range=time_range, limit=limit)
        return results.get("items", [])

    def get_user_top_artists(
        self, access_token: str, time_range: str = "medium_term", limit: int = 20
    ) -> list[dict[str, Any]]:
        """
        Get user's top artists (requires user authentication).

        Args:
            access_token: User's Spotify access token
            time_range: Time range (short_term, medium_term, long_term)
            limit: Maximum number of results

        Returns:
            List of user's top artists
        """
        client = self.get_auth_client(access_token)
        results = client.current_user_top_artists(time_range=time_range, limit=limit)
        return results.get("items", [])


# Global instance
_spotify_client: SpotifyClient | None = None


def get_spotify_client() -> SpotifyClient:
    """Get the global Spotify client instance."""
    global _spotify_client
    if _spotify_client is None:
        _spotify_client = SpotifyClient()
    return _spotify_client
