# TuneScore: Comprehensive Project Context

**Last Updated**: November 2, 2025

## 🎯 Project Overview

**TuneScore** is an AI-powered intelligence platform designed to bring data-driven insights to the music industry. It analyzes songs across multiple dimensions (audio, lyrics, market trends) to replace speculation with science. Think of it as "Bloomberg Terminal for Music."

### Vision
- Replace music industry gut-feel decisions with quantitative analysis
- Serve three distinct user tiers with tailored insights:
  - **Creators**: Artist/songwriters get song-level analysis (sonic genome, hooks, lyrical quality)
  - **Developers**: A&R scouts get talent discovery and predictive breakout scores
  - **Monetizers**: Label execs/investors get catalog valuations and market resonance

---

## 🏗️ Architecture Overview

### Three-Tier User Model

| Tier | Users | Key Features |
|------|-------|--------------|
| **Creator** | Artists, Songwriters | Sonic Genome, Lyrical Genome, Hook Lab, RIYL recommendations |
| **Developer** | A&R Scouts, Label Managers | Talent Discovery, Breakout Score, Collaboration Lab |
| **Monetizer** | Executives, Investors | Catalog Valuation, Global Resonance, Sync Licensing |

### Tech Stack

**Backend:**
- **Framework**: FastAPI (Python 3.12)
- **Database**: PostgreSQL 15+ with pgvector & pg_trgm extensions
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Logging**: structlog with PII guarding
- **Authentication**: JWT (access + refresh tokens)

**Frontend:**
- **Framework**: SvelteKit v2 with Svelte 5 runes
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Type Generation**: openapi-zod-client (generates TS types from backend API)
- **UI Library**: Custom components + lucide-svelte icons

**Audio/Music Processing:**
- **Audio Analysis**: librosa (spectral features, tempo, key detection)
- **Lyrical Analysis**: VADER (sentiment), sentence-transformers (embeddings)
- **Genre Detection**: Hugging Face transformers (ML-based hybrid detection)
- **Transcription**: OpenAI Whisper
- **Music Integrations**: Spotify API, YouTube Data API v3

**Infrastructure:**
- **Deployment**: Systemd services (no Docker)
- **Reverse Proxy**: Nginx/Caddy
- **Backups**: PostgreSQL pg_dump with rotation (7/30-day retention)
- **Logging**: /home/dwood/tunescore/logs/ with logrotate

---

## 📊 Core Analysis Engines

### 1. **Sonic Genome** (Audio Analysis)

Extracts comprehensive audio features from uploaded track files:

**Basic Features:**
- Tempo (BPM), Key (pitch), Duration, Loudness (dB)
- Energy (0-1), Danceability (0-1), Valence (0-1), Acousticness (0-1)
- Speechiness, Instrumentalness, Liveness

**Advanced Features:**
- Spectral Centroid (mean & std) - brightness of timbre
- Spectral Rolloff (mean & std) - high-frequency content
- Spectral Bandwidth (mean & std) - frequency spread
- Zero Crossing Rate (mean & std) - voice-like qualities
- RMS Energy (mean & std) - loudness consistency
- MFCCs (Mel-Frequency Cepstral Coefficients) - 13 timbre descriptors

**Quality Metrics:**
- Pitch Accuracy (0-100) - tuning consistency
- Timing Precision (0-100) - beat consistency
- Harmonic Coherence (0-100) - chord clarity

**Hook Detection:**
- Energy envelope + novelty curve analysis
- Identifies 15-second "viral segment"
- Hook Score (0-100) measures potential memorability

**Storage**: All data stored in JSONB `sonic_genome` field in `Analysis` table

### 2. **Lyrical Genome** (Text Analysis)

Analyzes lyrics for structure, sentiment, and quality:

**Sentiment Analysis:**
- Overall sentiment (positive/negative/neutral)
- Emotional arc - line-by-line sentiment scores
- Compound sentiment (-1 to +1)

**Structure Detection:**
- **Explicit markers**: Detects `[Verse 1]`, `[Chorus]`, `[Bridge]` etc.
- **Heuristic fallback** (NEW): Splits by blank lines, identifies repeated sections as choruses, assigns section types
- Section counts (e.g., "2 verses, 2 choruses, 1 bridge")
- Structure pattern (e.g., "verse → chorus → verse → chorus → bridge → chorus")

**Thematic Analysis:**
- Keyword-based theme detection (love, heartbreak, empowerment, nostalgia, spirituality, nature, etc.)
- Top 5 themes extracted

**Complexity Metrics:**
- Vocabulary Richness (unique words / total words)
- Unique Word Count
- Rhyme Density (estimated rhyme detection)
- Average Line Length (words per line)

**Repetition Analysis:**
- Repetition Score (0-100) - how repetitive is the hook?
- Most repeated phrase
- Strong Hook indicator (yes/no)

**Songwriting Quality Score:**
- Lyrical Craft (0-25)
- Narrative Arc (0-25)
- Structure Quality (0-25)
- Hook Effectiveness (0-25)
- **Total**: 0-100 with letter grade (A+, A, B+, B, C+, etc.)

**Storage**: All data stored in JSONB `lyrical_genome` field

### 3. **TuneScore** (Composite Ranking)

A composite score combining audio and lyrical analysis:

**Components:**
- Musicality (21/25 = 84%) - production + audio quality
- Hook Potential (5/15 = 32%) - viral segment + repetition
- Lyrical Quality (18/20 = 90%) - songwriting quality
- Commercial Appeal (8/10 = 77%) - market viability heuristics
- Production Quality (28/30 = 93%) - audio clarity + mixing

**Final Score:**
- 0-100 scale with letter grades (A+, A, B+, B, C+, C, D, F)
- Example: 79 = B+ ("Solid track with good market viability")
- Includes actionable insights and recommendations

### 4. **Genre Detection** (Hybrid ML + Heuristics)

Three-method approach:

**Method 1: Sonic Heuristics**
- Energy + Danceability + Acousticness → genre probabilities
- Fast, zero-cost fallback

**Method 2: ML-based (Hugging Face Transformers)**
- Pre-trained models for genre classification
- Instrument detection ensemble (violin, drums, guitar, etc.)
- Combines predictions weighted by confidence

**Method 3: Lyrical Cues**
- Theme keywords → genre hints
- Combined with sonic analysis

**Result**: `genre_predictions` with:
- Primary genre
- Top 3 genre predictions with confidence scores
- Detection method used
- Instrument composition (if available)

---

## 🎵 Database Schema

### Core Tables

```
users
  ├── id (PK)
  ├── email (unique)
  ├── password_hash
  └── created_at, updated_at

artists
  ├── id (PK)
  ├── name
  ├── spotify_id
  ├── youtube_channel_id
  └── metadata (JSONB)

tracks
  ├── id (PK)
  ├── title
  ├── artist_id (FK)
  ├── duration
  ├── spotify_id
  ├── user_id (FK)
  └── created_at, updated_at

track_assets
  ├── id (PK)
  ├── track_id (FK, unique)
  ├── audio_path
  ├── audio_format
  ├── lyrics_text
  └── upload_date

analyses
  ├── id (PK)
  ├── track_id (FK)
  ├── sonic_genome (JSONB) ← Audio analysis
  ├── lyrical_genome (JSONB) ← Lyrics analysis
  ├── hook_data (JSONB) ← Hook detection
  ├── tunescore (JSONB) ← Composite score
  ├── genre_predictions (JSONB) ← Genre analysis
  ├── quality_metrics (JSONB) ← Quality scores
  └── created_at

embeddings
  ├── id (PK)
  ├── track_id (FK, unique)
  ├── vector (vector/pgvector) ← 384-dim embeddings
  ├── created_at, updated_at

metrics_daily
  ├── id (PK)
  ├── track_id (FK)
  ├── platform (spotify/youtube)
  ├── metric_data (JSONB)
  ├── snapshot_date
```

---

## 📡 API Architecture

### Base URL
- **Development**: `http://localhost:8001`
- **Production**: `https://music.quilty.app`
- **API Version**: `/api/v1`
- **OpenAPI Docs**: `/api/v1/docs` (Swagger UI)

### Key Endpoints

**Track Management:**
```
POST   /api/v1/tracks/upload              Upload audio + lyrics → analyze
GET    /api/v1/tracks                     List all tracks
GET    /api/v1/tracks/{id}                Get track with full analysis
GET    /api/v1/tracks/{id}/analysis       Get analysis only
GET    /api/v1/tracks/{id}/status         Check analysis progress
```

**Search & Recommendations:**
```
GET    /api/v1/search/riyl/{track_id}     RIYL recommendations (vector-based)
GET    /api/v1/search/similar/{track_id}  Similar tracks by embedding
GET    /api/v1/search/query?q=...         Semantic text search
```

**External Integrations:**
```
GET    /api/v1/integrations/spotify/auth-url    OAuth authorization
GET    /api/v1/integrations/spotify/callback    OAuth callback
GET    /api/v1/integrations/spotify/track/{id}  Fetch Spotify track data
```

**Response Format:**
```json
{
  "id": 11,
  "title": "The Devil Went Down to Georgia",
  "artist_name": "The Charlie Daniels Band",
  "duration": 214,
  "spotify_id": "...",
  "sonic_genome": { /* audio analysis */ },
  "lyrical_genome": { /* lyrics analysis */ },
  "hook_data": { /* hook detection */ },
  "tunescore": { /* composite score */ },
  "genre_predictions": { /* genre analysis */ },
  "quality_metrics": { /* quality scores */ },
  "lyrics": "Full lyrics text...",
  "created_at": "2025-11-01T...",
  "updated_at": "2025-11-01T..."
}
```

---

## 🎨 Frontend Architecture

### Project Structure
```
frontend/
├── src/
│   ├── routes/
│   │   ├── +layout.svelte          Root layout
│   │   ├── +page.svelte            Dashboard
│   │   ├── upload/
│   │   │   ├── +page.svelte        Upload wizard
│   │   │   └── +page.server.ts     Server actions
│   │   ├── tracks/
│   │   │   └── [id]/
│   │   │       ├── +page.svelte    Track detail view
│   │   │       └── +page.server.ts Data loading
│   │   ├── dashboard/
│   │   │   └── +page.svelte        User dashboard
│   │   └── login/
│   │       └── +page.svelte        Auth pages
│   ├── lib/
│   │   ├── api/
│   │   │   ├── client.ts           Generated API client
│   │   │   └── schemas.ts          Generated types (from OpenAPI)
│   │   ├── components/
│   │   │   ├── ui/                 Reusable UI components
│   │   │   ├── TrackCard.svelte
│   │   │   ├── SonicGenomeCard.svelte
│   │   │   └── SectionBreakdown.svelte
│   │   ├── stores/                 State management
│   │   └── utils/
│   │       ├── formatters.ts       Data formatting utilities
│   │       └── validation.ts       Form validation
│   └── app.css                     Global styles
├── svelte.config.js
├── tailwind.config.js
└── tsconfig.json
```

### Key Pages

**1. Dashboard (`/dashboard`)**
- List of uploaded tracks
- Quick stats (total tracks, avg TuneScore, etc.)
- Recent analysis activity
- Upload new track button

**2. Track Detail (`/tracks/[id]`)**
- Full track analysis display
- Interactive sections:
  - TuneScore Breakdown (with insights)
  - Sonic Genome (with progress bars for audio features)
  - Lyrical Genome (sentiment, themes, structure)
  - **Song Sections Breakdown** (verse/chorus/bridge with collapsible lyrics)
  - Advanced Audio Features (spectral, MFCC, etc.)
  - Quality Metrics (pitch/timing/harmonic coherence)
  - Emotional Arc (line-by-line sentiment chart)
  - Hook Detection (viral segment time, score)
  - RIYL Recommendations (vector-based similar tracks)
  - Similar Tracks (content-based recommendations)

**3. Upload Wizard (`/upload`)**
- Drag-drop audio upload
- Optional lyrics paste/file upload
- Auto-transcription toggle (via Whisper)
- Metadata entry (artist, title, genre)
- Real-time analysis progress

### Type Generation Pipeline
```bash
# Backend generates OpenAPI schema
# Frontend pulls and generates TS types:
npm run schema:pull    # Download OpenAPI.json
npm run schema:gen     # Generate TypeScript types with zod validation
```

**Result**: Full type safety without manual DTO creation

---

## 🔄 Data Flow

### Upload → Analysis Pipeline

```
1. User uploads:
   - Audio file (.mp3, .wav, .flac, etc.)
   - Lyrics (paste, file, or auto-transcribe)
   - Metadata (title, artist, etc.)

2. Backend processes:
   a) Audio Feature Extraction
      - librosa extracts 100+ sonic features
      - Hook detection identifies viral segments
      - Quality metrics (pitch, timing, harmonic coherence)
      - Result: sonic_genome JSONB
   
   b) Lyrical Analysis
      - VADER sentiment + emotional arc
      - Section detection (explicit markers or heuristic fallback)
      - Theme extraction + complexity metrics
      - Songwriting quality scoring
      - Result: lyrical_genome JSONB
   
   c) TuneScore Calculation
      - Combines sonic + lyrical data
      - Generates grade (A+ to F) + insights
      - Result: tunescore JSONB
   
   d) Genre Detection
      - Sonic heuristics + ML ensemble + lyrical cues
      - Instrument detection
      - Result: genre_predictions JSONB
   
   e) Embedding Generation
      - sentence-transformers(MiniLM-L6-v2)
      - Encodes: title + lyrics + themes + artist
      - Stored in pgvector for RIYL search
      - Result: 384-dim vector in embeddings table

3. Frontend displays:
   - All analysis results
   - Interactive visualizations
   - Recommendations (RIYL, similar tracks)
```

---

## 🚀 Recent Enhancements

### November 2, 2025: Song Sections Breakdown

**Problem**: Lyrics without explicit `[Verse]` markers weren't showing sections

**Solution**: 
1. Added **heuristic section detection** algorithm:
   - Detects blank lines as section boundaries
   - Uses repetition detection to identify choruses
   - Auto-assigns section types (verse, chorus, bridge, intro, outro)

2. **Enhanced Frontend**:
   - New "Song Sections Breakdown" UI component
   - Collapsible/expandable sections
   - Shows section type, line count, and full lyrics

3. **Results**:
   - Track 11 now shows 9 detected sections
   - Songwriting quality improved from 62 → 75
   - Structure quality improved from 9/25 → 23/25

4. **Backend Improvements**:
   - Created Python virtual environment (`backend/venv`)
   - Installed all dependencies via Poetry
   - Re-analyzed track 11 with new algorithm

---

## 🔐 Security & Authentication

### Authentication Flow
```
1. User signs up → bcrypt hash password → JWT issued
2. Login → verify password → issue access + refresh tokens
3. API calls include: Authorization: Bearer <access_token>
4. Refresh flow → issue new token pair automatically
```

### Rate Limiting
- General: 300 requests/minute per IP
- Authentication: 50 requests/minute per IP
- Prevents brute force + API abuse

### Security Headers
- HSTS (HTTP Strict Transport Security)
- CSP (Content Security Policy)
- X-Frame-Options (clickjacking protection)
- X-Content-Type-Options (MIME sniffing prevention)

### Data Protection
- PII guarded in structured logs
- API keys stored in `.env` (not in code)
- No secrets committed to repo
- Cost governors for AI API usage

---

## 📊 Deployment

### Local Development
```bash
cd /home/dwood/tunescore

# Backend
cd backend
source venv/bin/activate
poetry install
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

### Production (Systemd)
```bash
# Services
/etc/systemd/system/tunescore-backend.service
/etc/systemd/system/tunescore-frontend.service  (optional)
/etc/systemd/system/tunescore-backup.service
/etc/systemd/system/tunescore-backup.timer

# Nginx reverse proxy
/etc/nginx/sites-available/tunescore.conf
```

### Database Backups
```bash
# Automatic: Daily via systemd timer
# Manual: 
pg_dump -Fc tunescore > backups/tunescore_$(date +%F).dump
pg_restore -d tunescore backups/tunescore_YYYY-MM-DD.dump

# Retention: 7 days daily + 30 days monthly
```

---

## 🛠️ Development Workflow

### Code Quality
```bash
cd backend

# Format code
poetry run black .

# Lint
poetry run ruff check .

# Type check
poetry run mypy app/

# Run tests
poetry run pytest
```

### Database Migrations
```bash
# Create migration
poetry run alembic revision -m "Add new feature"

# Apply latest
poetry run alembic upgrade head

# Rollback one
poetry run alembic downgrade -1

# View history
poetry run alembic history
```

### Frontend Type Generation
```bash
cd frontend

# Download latest OpenAPI schema
npm run schema:pull

# Generate TypeScript types + Zod validators
npm run schema:gen

# Build
npm run build

# Deploy to production
npm run deploy
```

---

## 📈 Roadmap

### Phase 0: Foundation ✅ DONE
- Monorepo structure
- PostgreSQL with extensions
- FastAPI skeleton + auth
- Core data models

### Phase 1: Sonic & Lyrical Genome ✅ MOSTLY DONE
- [x] Audio feature extraction
- [x] Hook detection
- [x] Lyrical analysis with VADER
- [x] Structure detection (explicit markers + heuristic)
- [x] Embeddings + RIYL search
- [x] Genre detection (hybrid ML + heuristics)
- [ ] Local LLM for thematic extraction (optional enhancement)

### Phase 2: Advanced Audio Analysis 📋 PLANNED (5 weeks)
**Status**: Planning complete, ready for implementation

**Bundle A: Quick Wins** (Weeks 1-2)
- [ ] Mastering Quality Detection (LUFS, DR scoring) - Priority: 4.0
- [ ] Chord Progression Analysis (basic-pitch) - Priority: 3.0
- [ ] AI Lyric Critic (Claude/GPT-4) - Priority: 2.7

**Bundle B: Vocal Intelligence** (Weeks 3-5)
- [ ] Vocal Isolation (Spleeter) - Priority: 2.25
- [ ] TikTok Virality Predictor - Priority: 2.25

**Documentation**: See `docs/ADVANCED_FEATURES_SUMMARY.md` for full plan

### Phase 3: A&R Intelligence 🔄 IN PROGRESS
- [x] Spotify OAuth integration
- [x] YouTube API integration
- [ ] Nightly metrics snapshots
- [ ] Breakout Score v1 (predictive 7/14/28-day velocity)
- [ ] Collaboration Lab (feature interaction modeling)

### Phase 4: Monetization & Catalog 📋 PLANNED
- [ ] Catalog valuation (DCF model)
- [ ] Global market resonance scoring
- [ ] Sync licensing matcher

### Phase 5: Frontend Polish 🎨 IN PROGRESS
- [x] SvelteKit scaffold
- [x] Upload wizard
- [x] Track detail dashboard
- [x] Song Sections Breakdown (NEW)
- [ ] A&R dashboard
- [ ] Catalog manager interface
- [ ] Mobile responsive improvements

---

## 🤝 Contributing & Communication

### For AI Assistants (ChatGPT, Claude, etc.)

When discussing this project:

1. **Code Style**: 
   - Follow Black formatting (88 char lines)
   - Use type hints (mypy strict-ish mode)
   - PEP 8 conventions
   - Clean, senior-level code only

2. **Database**:
   - Always use async SQLAlchemy
   - JSONB for flexible data (sonic_genome, lyrical_genome, etc.)
   - pgvector for embeddings
   - Never break migrations—create new ones

3. **Frontend**:
   - Never hand-roll DTOs; use generated types from OpenAPI
   - Svelte 5 runes (not stores where possible)
   - Tailwind for styling
   - Responsive design by default

4. **API Design**:
   - RESTful with /api/v1 prefix
   - Proper HTTP status codes
   - Error format: `{error: {code, message}}`
   - OpenAPI docs auto-generated

5. **Logging**:
   - Use structlog for structured logging
   - Guard PII in logs
   - Log all AI prompts to `logs/api_prompts.log`

6. **Music Industry Domain**:
   - Understand three tiers (Creator/Developer/Monetizer)
   - Know audio feature meanings (energy, danceability, valence, etc.)
   - Familiar with Spotify/YouTube integrations
   - RIYL = "Recommended If You Like" recommendations

---

## 📚 Key Resources

### Code & Infrastructure
- **Backend Entry**: `/home/dwood/tunescore/backend/app/main.py`
- **Frontend Entry**: `/home/dwood/tunescore/frontend/src/routes/+page.svelte`
- **API Docs**: Generated at `/api/v1/docs`
- **Database**: PostgreSQL, connection string in `.env`
- **Logs**: `/home/dwood/tunescore/logs/`
- **Backups**: `/home/dwood/tunescore/backups/`

### Planning & Documentation
- **Advanced Features Plan**: `docs/ADVANCED_FEATURES_SUMMARY.md` (start here)
- **Feature Prioritization**: `docs/FEATURE_PRIORITIZATION.md`
- **Implementation Roadmap**: `docs/IMPLEMENTATION_ROADMAP.md`
- **Technical Briefs**: `docs/features/` (5 detailed feature specs)
- **Quick Reference**: `docs/QUICK_REFERENCE.md` (60-second overview)
- **Full Index**: `docs/FEATURES_INDEX.md` (navigation guide)

---

## 🆕 Recent Updates

### November 2, 2025: Advanced Features Planning Complete
- ✅ Audited audio/ML stack (15 KB documentation)
- ✅ Prioritized 20 features using impact/effort scoring
- ✅ Created technical briefs for top 5 features (56 KB)
- ✅ Defined 5-week implementation roadmap
- ✅ Projected 900% 3-year ROI, 4-month payback
- 📋 **Next**: Stakeholder approval, begin prototyping

### November 2, 2025: Song Sections Breakdown
- Added heuristic section detection algorithm
- Enhanced Frontend with collapsible sections UI
- Track 11 now shows 9 detected sections
- Songwriting quality improved from 62 → 75

---

**TuneScore** - Replacing speculation with science in music. 🎵🚀
