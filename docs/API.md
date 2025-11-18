# TuneScore API Documentation

## Base URL

```
http://localhost:8001/api/v1
```

## Interactive Documentation

- **Swagger UI**: http://localhost:8001/api/v1/docs
- **ReDoc**: http://localhost:8001/api/v1/redoc
- **OpenAPI JSON**: http://localhost:8001/api/v1/openapi.json

---

## Authentication

Currently, authentication is scaffolded but not enforced. JWT authentication will be required for production endpoints.

---

## Endpoints

### Health Check

#### `GET /api/v1/health`

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "tunescore-api"
}
```

---

## Tracks

### Upload Track

#### `POST /api/v1/tracks/upload`

Upload a track with audio file and/or lyrics for analysis.

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `track_data` (form field, required): JSON string with track metadata
    ```json
    {
      "title": "Song Title",
      "artist_name": "Artist Name",
      "genre": "Pop",
      "release_date": "2025-01-01T00:00:00Z",
      "lyrics": "Optional lyrics text..."
    }
    ```
  - `audio_file` (file, optional): Audio file (mp3, wav, flac, m4a, ogg)
  - `lyrics_file` (file, optional): Lyrics text file

**Response:**
```json
{
  "track": {
    "id": 1,
    "title": "Song Title",
    "artist_name": "Artist Name",
    "genre": "Pop",
    "release_date": "2025-01-01T00:00:00Z",
    "lyrics": "...",
    "created_at": "2025-10-31T08:00:00Z",
    "updated_at": "2025-10-31T08:00:00Z"
  },
  "analysis_started": true,
  "message": "Track uploaded and analyzed successfully"
}
```

### Get Track

#### `GET /api/v1/tracks/{track_id}`

Retrieve track information.

**Response:**
```json
{
  "id": 1,
  "title": "Song Title",
  "artist_name": "Artist Name",
  "genre": "Pop",
  "release_date": "2025-01-01T00:00:00Z",
  "lyrics": "...",
  "created_at": "2025-10-31T08:00:00Z",
  "updated_at": "2025-10-31T08:00:00Z"
}
```

### Get Track Analysis

#### `GET /api/v1/tracks/{track_id}/analysis`

Get the latest analysis results for a track.

**Response:**
```json
{
  "track_id": 1,
  "audio_features": {
    "duration_s": 180.5,
    "tempo": 120.0,
    "rms": 0.15,
    "zero_crossing_rate": 0.05,
    "mfcc_mean": [/* 13 values */],
    "mfcc_std": [/* 13 values */],
    "chroma_mean": [/* 12 values */],
    "spectral_centroid_mean": 2500.0,
    "spectral_bandwidth_mean": 2000.0,
    "harmonic_ratio": 0.65,
    "danceability_approx": 0.75,
    "energy_approx": 0.80,
    "valence_approx": 0.60,
    "loudness_approx": -5.0,
    "key_approx": 5
  },
  "lyrical_analysis": {
    "overall_sentiment": {
      "compound": 0.5,
      "pos": 0.3,
      "neu": 0.5,
      "neg": 0.2
    },
    "emotional_arc": [/* sentiment per segment */],
    "themes": ["love", "hope", "celebration"],
    "potential_hooks": ["Chorus line 1", "Chorus line 2"]
  },
  "hook_detection": {
    "start_time_s": 45.0,
    "end_time_s": 60.0,
    "hook_score": 0.85
  },
  "created_at": "2025-10-31T08:00:00Z",
  "updated_at": "2025-10-31T08:00:00Z"
}
```

---

## Search & RIYL

### Get RIYL Recommendations

#### `GET /api/v1/search/riyl/{track_id}`

Get "Recommended If You Like" recommendations for a track.

**Query Parameters:**
- `limit` (int, optional): Number of recommendations (default: 5, max: 20)

**Response:**
```json
{
  "reference_track": {
    "id": 1,
    "title": "Song Title",
    "artist_name": "Artist Name"
  },
  "recommendations": [
    {
      "track_id": 2,
      "title": "Similar Song",
      "artist_name": "Similar Artist",
      "similarity_score": 0.892,
      "spotify_id": "..."
    }
  ],
  "count": 5,
  "message": "Found 5 similar tracks"
}
```

### Find Similar Tracks

#### `GET /api/v1/search/similar/{track_id}`

Find tracks similar to the given track.

**Query Parameters:**
- `limit` (int, optional): Number of results (default: 10, max: 50)
- `min_similarity` (float, optional): Minimum similarity score (default: 0.5, range: 0.0-1.0)

**Response:**
```json
[
  {
    "track_id": 2,
    "title": "Similar Song",
    "artist_name": "Similar Artist",
    "similarity_score": 0.892,
    "spotify_id": "..."
  }
]
```

### Search by Text

#### `GET /api/v1/search/query`

Search for tracks using a text query (semantic search).

**Query Parameters:**
- `q` (string, required): Search query (e.g., "sad love songs", "upbeat party music")
- `limit` (int, optional): Number of results (default: 10, max: 50)
- `min_similarity` (float, optional): Minimum similarity score (default: 0.3)

**Response:**
```json
[
  {
    "track_id": 1,
    "title": "Matching Song",
    "artist_name": "Artist Name",
    "similarity_score": 0.756,
    "spotify_id": "..."
  }
]
```

---

## Spotify Integration

### Get Spotify Auth URL

#### `GET /api/v1/integrations/spotify/auth-url`

Get the Spotify OAuth authorization URL for user authentication.

**Response:**
```json
{
  "auth_url": "https://accounts.spotify.com/authorize?...",
  "message": "Visit this URL to authorize Spotify access"
}
```

### Spotify OAuth Callback

#### `GET /api/v1/integrations/spotify/callback`

Handle Spotify OAuth callback (exchange authorization code for access token).

**Query Parameters:**
- `code` (string, required): Authorization code from Spotify

**Response:**
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "expires_in": 3600,
  "message": "Successfully authenticated with Spotify"
}
```

### Get Spotify Track

#### `GET /api/v1/integrations/spotify/track/{track_id}`

Get track information from Spotify.

**Response:** Spotify track object (see Spotify API docs)

### Get Spotify Audio Features

#### `GET /api/v1/integrations/spotify/track/{track_id}/audio-features`

Get pre-computed audio features for a Spotify track.

**Response:**
```json
{
  "danceability": 0.75,
  "energy": 0.80,
  "key": 5,
  "loudness": -5.0,
  "mode": 1,
  "speechiness": 0.05,
  "acousticness": 0.20,
  "instrumentalness": 0.00,
  "liveness": 0.10,
  "valence": 0.60,
  "tempo": 120.0,
  "duration_ms": 180500,
  "time_signature": 4
}
```

### Get Spotify Artist

#### `GET /api/v1/integrations/spotify/artist/{artist_id}`

Get artist information from Spotify.

**Response:** Spotify artist object (see Spotify API docs)

### Get Spotify Artist Stats

#### `GET /api/v1/integrations/spotify/artist/{artist_id}/stats`

Get artist statistics from Spotify.

**Response:**
```json
{
  "followers": 1000000,
  "popularity": 75,
  "genres": ["pop", "dance"],
  "external_urls": {
    "spotify": "https://open.spotify.com/artist/..."
  }
}
```

### Get Related Artists

#### `GET /api/v1/integrations/spotify/artist/{artist_id}/related`

Get artists related to the given artist (useful for RIYL).

**Response:** Array of Spotify artist objects

### Search Spotify Tracks

#### `GET /api/v1/integrations/spotify/search/track`

Search for tracks on Spotify.

**Query Parameters:**
- `q` (string, required): Search query
- `limit` (int, optional): Number of results (default: 10, max: 50)

**Response:** Array of Spotify track objects

### Search Spotify Artists

#### `GET /api/v1/integrations/spotify/search/artist`

Search for artists on Spotify.

**Query Parameters:**
- `q` (string, required): Search query
- `limit` (int, optional): Number of results (default: 10, max: 50)

**Response:** Array of Spotify artist objects

---

## YouTube Integration

### Get YouTube Video

#### `GET /api/v1/integrations/youtube/video/{video_id}`

Get video information from YouTube.

**Response:** YouTube video object (see YouTube Data API docs)

### Get YouTube Video Stats

#### `GET /api/v1/integrations/youtube/video/{video_id}/stats`

Get video statistics from YouTube.

**Response:**
```json
{
  "view_count": 1000000,
  "like_count": 50000,
  "comment_count": 5000,
  "favorite_count": 0
}
```

### Get YouTube Channel

#### `GET /api/v1/integrations/youtube/channel/{channel_id}`

Get channel information from YouTube.

**Response:** YouTube channel object (see YouTube Data API docs)

### Get YouTube Channel Stats

#### `GET /api/v1/integrations/youtube/channel/{channel_id}/stats`

Get channel statistics from YouTube.

**Response:**
```json
{
  "subscriber_count": 500000,
  "view_count": 10000000,
  "video_count": 100
}
```

### Search YouTube Videos

#### `GET /api/v1/integrations/youtube/search/video`

Search for videos on YouTube.

**Query Parameters:**
- `q` (string, required): Search query
- `limit` (int, optional): Number of results (default: 10, max: 50)
- `order` (string, optional): Sort order (date, rating, relevance, title, videoCount, viewCount)

**Response:** Array of YouTube video search results

### Search YouTube Channels

#### `GET /api/v1/integrations/youtube/search/channel`

Search for channels on YouTube.

**Query Parameters:**
- `q` (string, required): Search query
- `limit` (int, optional): Number of results (default: 10, max: 50)

**Response:** Array of YouTube channel search results

### Get Trending Music

#### `GET /api/v1/integrations/youtube/trending/music`

Get trending music videos on YouTube.

**Query Parameters:**
- `region` (string, optional): ISO 3166-1 alpha-2 country code (default: "US")
- `limit` (int, optional): Number of results (default: 10, max: 50)

**Response:** Array of trending music videos

---

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK`: Success
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error response format:
```json
{
  "detail": "Error message"
}
```

---

## Rate Limiting

- General endpoints: 300 requests per minute
- Authentication endpoints: 50 requests per minute

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Time when limit resets

---

## CORS

CORS is enabled for the following origins (configurable via environment):
- `http://localhost:5128`
- `http://127.0.0.1:5128`
- Additional origins can be configured via `BACKEND_CORS_ORIGINS` environment variable

---

*Last Updated: October 31, 2025*

