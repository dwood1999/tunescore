# TuneScore Setup Guide

## System Dependencies

### FFmpeg (Required for Audio Processing)

FFmpeg is required for librosa to process audio files.

**Install on Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y ffmpeg
```

**Verify installation:**
```bash
ffmpeg -version
```

### PostgreSQL (Already Installed)

PostgreSQL 18 with pg_trgm extension is already configured.

### Python 3.12 (Already Installed)

Python 3.12 is already available on this system.

## Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd /home/dwood/tunescore/backend
   ```

2. **Install dependencies with Poetry:**
   ```bash
   poetry install
   ```

3. **Run database migrations:**
   ```bash
   poetry run alembic upgrade head
   ```

4. **Start the backend:**
   ```bash
   ../scripts/start_backend.sh
   # Or manually:
   poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
   ```

5. **Access API documentation:**
   - Swagger UI: http://localhost:8001/api/v1/docs
   - ReDoc: http://localhost:8001/api/v1/redoc
   - OpenAPI JSON: http://localhost:8001/api/v1/openapi.json

## Testing the API

### Upload a Track

```bash
curl -X POST "http://localhost:8001/api/v1/tracks/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "title=My Song" \
  -F "artist_name=Test Artist" \
  -F "lyrics=This is a test song..." \
  -F "audio_file=@/path/to/audio.mp3"
```

### Get Track Details

```bash
curl "http://localhost:8001/api/v1/tracks/1"
```

### Get Analysis Results

```bash
curl "http://localhost:8001/api/v1/tracks/1/analysis"
```

## Troubleshooting

### "FFmpeg not found" error

Install FFmpeg as described above.

### Database connection errors

Ensure PostgreSQL is running:
```bash
sudo systemctl status postgresql
```

Check DATABASE_URL in `/home/dwood/tunescore/.env`:
```
DATABASE_URL=postgresql+asyncpg://dwood@/tunescore
```

### Import errors

Clear Python cache and reinstall:
```bash
cd /home/dwood/tunescore/backend
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
poetry install
```
