# TuneScore Quick Start Guide

## 🚀 Start in 3 Steps

### 1. Start the Backend

```bash
cd /home/dwood/tunescore
./scripts/start_backend.sh
```

The API will be available at: http://localhost:8001

### 2. Open API Documentation

Visit: http://localhost:8001/api/v1/docs

### 3. Upload Your First Track

```bash
curl -X POST "http://localhost:8001/api/v1/tracks/upload" \
  -F 'track_data={"title":"My Song","artist_name":"My Artist"}' \
  -F "audio_file=@/path/to/song.mp3"
```

---

## 📋 Common Commands

### Backend Management

```bash
# Start backend
./scripts/start_backend.sh

# Check if running
curl http://localhost:8001/api/v1/health

# View logs
tail -f logs/api_prompts.log
```

### Database Operations

```bash
# Connect to database
psql -U dwood tunescore

# Run migrations
cd backend && poetry run alembic upgrade head

# Backup database
./scripts/backup_db.sh

# Restore database
./scripts/restore_db.sh backups/tunescore_backup_YYYYMMDD_HHMMSS.sql.gz
```

### Track Operations

```bash
# Upload track
curl -X POST "http://localhost:8001/api/v1/tracks/upload" \
  -F 'track_data={"title":"Song Title","artist_name":"Artist Name"}' \
  -F "audio_file=@song.mp3" \
  -F "lyrics_file=@lyrics.txt"

# Get track analysis
curl "http://localhost:8001/api/v1/tracks/1/analysis" | jq '.'

# Get RIYL recommendations
curl "http://localhost:8001/api/v1/search/riyl/1?limit=5" | jq '.'

# Search tracks
curl "http://localhost:8001/api/v1/search/query?q=sad+love+songs" | jq '.'
```

### Spotify Integration

```bash
# Get Spotify auth URL
curl "http://localhost:8001/api/v1/integrations/spotify/auth-url" | jq -r '.auth_url'

# Search Spotify tracks
curl "http://localhost:8001/api/v1/integrations/spotify/search/track?q=daft+punk" | jq '.'

# Get track audio features
curl "http://localhost:8001/api/v1/integrations/spotify/track/TRACK_ID/audio-features" | jq '.'

# Get related artists
curl "http://localhost:8001/api/v1/integrations/spotify/artist/ARTIST_ID/related" | jq '.'
```

### YouTube Integration

```bash
# Get video stats
curl "http://localhost:8001/api/v1/integrations/youtube/video/VIDEO_ID/stats" | jq '.'

# Get channel stats
curl "http://localhost:8001/api/v1/integrations/youtube/channel/CHANNEL_ID/stats" | jq '.'

# Search videos
curl "http://localhost:8001/api/v1/integrations/youtube/search/video?q=music+video" | jq '.'

# Get trending music
curl "http://localhost:8001/api/v1/integrations/youtube/trending/music?region=US" | jq '.'
```

---

## 🔧 Configuration

### Environment Variables

Copy and edit the environment template:

```bash
cp env.template .env
nano .env
```

**Required:**
- `DATABASE_URL` - PostgreSQL connection
- `JWT_SECRET` - Random secret key

**Optional:**
- `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`
- `YOUTUBE_API_KEY`
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| `README.md` | Project overview |
| `STATUS.md` | Current status and features |
| `SUMMARY.md` | Comprehensive summary |
| `QUICKSTART.md` | This file - quick reference |
| `docs/SETUP.md` | Installation guide |
| `docs/API.md` | Complete API reference |
| `docs/DEPLOYMENT.md` | Production deployment |
| `docs/PROGRESS.md` | Implementation progress |

---

## 🏥 Health Checks

```bash
# Basic health
curl http://localhost:8001/api/v1/health

# Detailed health (includes database check)
curl http://localhost:8001/api/v1/health/detailed | jq '.'

# Readiness probe
curl http://localhost:8001/api/v1/health/ready

# Liveness probe
curl http://localhost:8001/api/v1/health/live

# Metrics
curl http://localhost:8001/api/v1/health/metrics | jq '.'
```

---

## 🐛 Troubleshooting

### Backend won't start?

```bash
# Check database connection
psql -U dwood tunescore -c "SELECT 1"

# Check Python environment
cd backend && poetry run python --version

# Check dependencies
cd backend && poetry install
```

### Can't upload audio files?

```bash
# Check FFmpeg installation
ffmpeg -version

# Install if missing
sudo apt install ffmpeg

# Check storage directory
ls -ld files/
mkdir -p files/audio files/lyrics
```

### Database issues?

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check database exists
psql -U dwood -l | grep tunescore

# Run migrations
cd backend && poetry run alembic upgrade head
```

---

## 💡 Pro Tips

1. **Use jq** for pretty JSON output: `curl ... | jq '.'`
2. **Check logs** for errors: `tail -f logs/api_prompts.log`
3. **Test with Swagger UI** at http://localhost:8001/api/v1/docs
4. **Backup regularly** with `./scripts/backup_db.sh`
5. **Monitor health** with `/api/v1/health/detailed`

---

## 🎯 What's Working

✅ Track upload with audio and lyrics  
✅ Automatic audio analysis (tempo, key, energy, etc.)  
✅ Hook detection (15-second viral segment)  
✅ Lyrics sentiment analysis  
✅ Semantic search and RIYL recommendations  
✅ Spotify integration (tracks, artists, features)  
✅ YouTube integration (videos, channels, stats)  
✅ Health checks and monitoring  
✅ Automated backups  

---

## 📞 Need Help?

- **API Docs**: http://localhost:8001/api/v1/docs
- **Full Docs**: See `docs/` directory
- **Logs**: Check `logs/api_prompts.log`
- **Database**: `psql -U dwood tunescore`

---

**Happy Music Analysis! 🎵**

*Last Updated: October 31, 2025*

