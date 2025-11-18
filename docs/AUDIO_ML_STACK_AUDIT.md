# TuneScore: Audio/ML Stack Audit

**Date**: November 2, 2025  
**Purpose**: Inventory existing capabilities and identify reusable components for advanced feature development

---

## 🎯 Executive Summary

TuneScore has a **solid foundation** for advanced audio analysis. The platform currently leverages:
- **librosa** for comprehensive audio feature extraction (100+ features)
- **PyTorch + Hugging Face Transformers** for ML-based genre/instrument detection
- **sentence-transformers** for semantic embeddings and RIYL recommendations
- **VADER** for lyrical sentiment analysis
- **OpenAI Whisper** for audio transcription

**Key Strengths**:
- Async SQLAlchemy 2.0 with JSONB storage (zero-transform principle)
- pgvector for semantic search
- Modular service architecture (easy to extend)
- Quality metrics already implemented (pitch, timing, harmonic coherence)

**Gaps for Advanced Features**:
- No vocal isolation (Spleeter/Demucs)
- No chord progression extraction (Chordino/basic-pitch)
- No mastering quality analysis (pyloudnorm)
- No stem-level mixing analysis
- No AI authenticity detection

---

## 📦 Current Dependencies (from pyproject.toml)

### Audio Processing
```toml
librosa = "^0.10.0"           # Core audio analysis
soundfile = "^0.12.1"         # Audio I/O
pydub = "^0.25.1"             # Audio manipulation
numpy = "^1.26.0"             # Numerical computing
scipy = "^1.11.0"             # Scientific computing
```

### Machine Learning
```toml
transformers = "^4.35.0"      # Hugging Face models (genre/instrument)
torch = "^2.1.0"              # PyTorch backend
torchaudio = "^2.1.0"         # Audio ML utilities
sentence-transformers = "^2.2.0"  # Embeddings (MiniLM-L6-v2)
```

### NLP/Lyrics
```toml
vaderSentiment = "^3.3.2"     # Sentiment analysis
```

### Integrations
```toml
spotipy = "^2.23.0"           # Spotify API
google-api-python-client = "^2.100.0"  # YouTube API
```

### AI Services (Optional)
```toml
anthropic = "^0.40.0"         # Claude API
openai = "^1.58.0"            # GPT/Whisper
openai-whisper = "^20250625"  # Audio transcription
```

### Commented Out (Not Yet Installed)
```toml
# essentia-tensorflow = "^2.1b6"  # 100+ audio extractors
# madmom = "^0.16.1"              # Beat tracking
# demucs = "^4.0.1"               # Source separation
```

---

## 🏗️ Current Architecture

### Service Layer Structure
```
backend/app/services/
├── audio/
│   ├── feature_extraction.py    # Sonic genome extraction (100+ features)
│   ├── instrument_detection.py  # ML-based instrument classification
│   └── transcription.py         # Whisper integration
├── classification/
│   ├── genre_detector.py        # Hybrid genre detection
│   └── genre_ml.py              # ML-based genre classification
├── embeddings/
│   ├── generator.py             # sentence-transformers embeddings
│   └── search.py                # pgvector semantic search
├── integrations/
│   ├── spotify.py               # Spotify OAuth + API
│   └── youtube.py               # YouTube Data API
├── lyrics/
│   └── analysis.py              # VADER sentiment + structure detection
├── scoring/
│   └── tunescore.py             # Composite scoring algorithm
└── similarity/
    └── artist_similarity.py     # Artist comparison
```

### Database Schema (JSONB Storage)
```sql
analyses
  ├── sonic_genome (JSONB)        # Audio features from librosa
  ├── lyrical_genome (JSONB)      # Lyrics analysis (VADER)
  ├── hook_data (JSONB)           # Hook detection (energy + novelty)
  ├── tunescore (JSONB)           # Composite score + insights
  ├── genre_predictions (JSONB)   # Genre + instrument detection
  └── quality_metrics (JSONB)     # Pitch/timing/harmonic coherence

embeddings
  └── vector (vector/pgvector)    # 384-dim MiniLM-L6-v2 embeddings
```

---

## 🎵 Existing Audio Analysis Capabilities

### 1. Sonic Genome (feature_extraction.py)

**Basic Features** (Spotify-like):
- Tempo (BPM), Key, Duration, Loudness
- Energy, Danceability, Valence, Acousticness
- Speechiness, Instrumentalness, Liveness

**Advanced Features** (Spectral Analysis):
- Spectral Centroid (brightness)
- Spectral Rolloff (high-frequency content)
- Spectral Bandwidth (frequency spread)
- Zero Crossing Rate (percussiveness)
- RMS Energy (loudness consistency)
- MFCCs (13 timbre descriptors)

**Quality Metrics** (0-100 scale):
- Pitch Accuracy (tuning consistency via piptrack)
- Timing Precision (beat consistency with syncopation awareness)
- Harmonic Coherence (chord clarity via chromagram)

**Hook Detection**:
- Energy envelope + novelty curve analysis
- Identifies 15-second "viral segment"
- Hook Score (0-100) for memorability

**Key Implementation Details**:
- Sample rate: 22050 Hz (librosa default)
- Context-aware metrics (distinguishes professional syncopation from poor timing)
- Electronic music detection (low rolloff + consistent dynamics)

### 2. Genre Detection (genre_detector.py, genre_ml.py)

**Three-Method Hybrid Approach**:

1. **Sonic Heuristics** (Fast, zero-cost fallback)
   - Energy + Danceability + Acousticness → genre probabilities
   
2. **ML-based (Hugging Face Transformers)**
   - Pre-trained models: `MIT/ast-finetuned-audioset-10-10-0.4593`
   - Instrument detection ensemble (violin, drums, guitar, etc.)
   - Weighted confidence scoring

3. **Lyrical Cues**
   - Theme keywords → genre hints
   - Combined with sonic analysis

**Output**: Primary genre + top 3 predictions with confidence scores

### 3. Lyrical Analysis (lyrics/analysis.py)

**Sentiment Analysis** (VADER):
- Overall sentiment (positive/negative/neutral)
- Emotional arc (line-by-line sentiment scores)
- Compound sentiment (-1 to +1)

**Structure Detection**:
- Explicit markers: `[Verse 1]`, `[Chorus]`, `[Bridge]`
- Heuristic fallback: Blank line splitting + repetition detection
- Section counts and pattern analysis

**Thematic Analysis**:
- Keyword-based theme detection (love, heartbreak, empowerment, etc.)
- Top 5 themes extracted

**Complexity Metrics**:
- Vocabulary Richness (unique words / total words)
- Rhyme Density (estimated rhyme detection)
- Average Line Length

**Songwriting Quality Score** (0-100):
- Lyrical Craft (0-25)
- Narrative Arc (0-25)
- Structure Quality (0-25)
- Hook Effectiveness (0-25)

### 4. Embeddings & RIYL (embeddings/generator.py)

**Model**: `sentence-transformers/all-MiniLM-L6-v2`
- 384-dimensional embeddings
- Encodes: title + lyrics + themes + artist
- Stored in pgvector for cosine similarity search

**Use Cases**:
- "Recommended If You Like" (RIYL) recommendations
- Semantic text search
- Similar track discovery

---

## 🔧 Reusable Components for Advanced Features

### 1. Audio Loading Pipeline
**Location**: `feature_extraction.py:load_audio()`
- Handles multiple formats (.mp3, .wav, .flac)
- Standardizes to 22050 Hz mono
- Error handling + logging

**Reuse For**: Vocal isolation, chord extraction, mastering analysis

### 2. JSONB Storage Pattern
**Location**: Database schema (`analyses` table)
- Zero-transform principle (store raw AI outputs)
- Flexible schema evolution
- No migration needed for new features

**Reuse For**: Store vocal analysis, chord progressions, mastering metrics

### 3. Async Processing Architecture
**Location**: `tracks.py` router + service layer
- FastAPI async endpoints
- SQLAlchemy 2.0 async sessions
- Background task support

**Reuse For**: Long-running vocal isolation, chord extraction jobs

### 4. Quality Metrics Framework
**Location**: `feature_extraction.py:extract_quality_metrics()`
- 0-100 scoring convention
- Grade mapping (Professional → Amateur)
- Rationale generation

**Reuse For**: Mastering quality scores, vocal performance scores

### 5. ML Model Loading Pattern
**Location**: `genre_ml.py`, `instrument_detection.py`
- Lazy loading (load on first use)
- Singleton pattern (reuse model instances)
- Error handling for missing models

**Reuse For**: Vocal isolation models, chord extraction models

### 6. Logging Infrastructure
**Location**: `structlog` setup in `main.py`
- Request ID tracking
- PII guarding
- Structured JSON logs

**Reuse For**: Log AI prompts, model inference times, feature extraction metrics

---

## 🚀 Infrastructure Readiness

### Compute Resources
- **CPU**: librosa, VADER, basic ML models ✅
- **GPU**: Optional for Transformers (currently CPU fallback) ⚠️
- **Memory**: Current models fit in <4GB RAM ✅

### Storage
- **PostgreSQL**: pgvector extension installed ✅
- **File Storage**: `/home/dwood/tunescore/backend/files/` ✅
- **Backups**: Nightly pg_dump with rotation ✅

### Deployment
- **Systemd Services**: Backend running on port 8001 ✅
- **Nginx Reverse Proxy**: Configured ✅
- **Logs**: `/home/dwood/tunescore/logs/` with logrotate ✅

### Missing Infrastructure
- **GPU Support**: Not configured (needed for Demucs, heavy Transformers) ❌
- **Job Queue**: No Celery/RQ for long-running tasks (using FastAPI background tasks) ⚠️
- **Model Cache**: No shared model cache (each process loads separately) ⚠️

---

## 🎯 Feature Compatibility Matrix

| Feature | Existing Components | New Dependencies | Complexity | GPU Required |
|---------|---------------------|------------------|------------|--------------|
| **Vocal Isolation** | Audio loading, JSONB storage | Spleeter/Demucs | Medium | Optional (Demucs) |
| **Chord Progression** | Audio loading, quality metrics | Chordino/basic-pitch | Low | No |
| **Mastering Quality** | Audio loading, quality framework | pyloudnorm | Low | No |
| **Stem Mixing Analysis** | Vocal isolation output | None (use librosa) | Medium | No |
| **AI Cover Detection** | Audio loading, ML patterns | WavLM/Wav2Vec 2.0 | High | Yes |
| **Lyrical Mood Board** | Lyrical genome, themes | DALL-E 3/Stable Diffusion API | Low | No (API) |
| **Reference Track Matching** | Embeddings, RIYL | None (extend existing) | Low | No |
| **TikTok Virality Predictor** | Hook detection, lyrics | None (extend existing) | Medium | No |
| **Career Trajectory Modeling** | Spotify integration | Prophet (Meta) | Medium | No |
| **Sync Licensing Matcher** | Genre detection, themes | Audio Spectrogram Transformer | Medium | Optional |
| **Beat & Flow Analysis** | Timing precision | Parselmouth (Praat) | Medium | No |
| **Mastering Reference Comparison** | Sonic genome | None (spectral diff) | Low | No |
| **Global Market Resonance** | Spotify/YouTube APIs | None (extend existing) | Low | No |
| **AI Lyric Critic** | Lyrical genome | Claude/GPT-4 (already installed) | Low | No (API) |

---

## 📊 Effort/Impact Quick Assessment

### Low-Hanging Fruit (High Impact, Low Effort)
1. **Mastering Quality Detection** (pyloudnorm + DR meter)
   - Effort: 1-2 days
   - Impact: Instant "pro mix quality" credibility
   - Dependencies: `pyloudnorm` (pip install)

2. **Chord Progression Analysis** (basic-pitch)
   - Effort: 2-3 days
   - Impact: Songwriting insights gold
   - Dependencies: `basic-pitch` (Spotify's model)

3. **Mastering Reference Comparison** (spectral diff)
   - Effort: 1 day
   - Impact: Actionable EQ suggestions
   - Dependencies: None (use existing librosa)

4. **AI Lyric Critic** (Claude/GPT-4)
   - Effort: 1-2 days
   - Impact: Creative tool for songwriters
   - Dependencies: Already installed (anthropic, openai)

### Medium Effort, High Impact
5. **Vocal Isolation** (Spleeter)
   - Effort: 3-5 days
   - Impact: Unlocks 10+ new analysis dimensions
   - Dependencies: `spleeter` (TensorFlow-based, CPU-friendly)

6. **TikTok Virality Predictor**
   - Effort: 3-4 days
   - Impact: Highly marketable feature
   - Dependencies: None (extend hook detection)

7. **Sync Licensing Matcher**
   - Effort: 4-5 days
   - Impact: Revenue-generating feature
   - Dependencies: `ast-finetuned-audioset` (already using similar models)

### High Effort, High Impact
8. **Vocal Isolation (Demucs - SOTA)**
   - Effort: 5-7 days (GPU setup + integration)
   - Impact: Best-in-class vocal separation
   - Dependencies: `demucs` (Meta's model, GPU recommended)

9. **AI Cover Detection** (WavLM)
   - Effort: 5-7 days
   - Impact: Unique differentiator
   - Dependencies: `transformers` (WavLM/Wav2Vec 2.0), GPU required

10. **Career Trajectory Modeling** (Prophet)
    - Effort: 5-7 days
    - Impact: Predictive A&R intelligence
    - Dependencies: `prophet` (Meta's time-series library)

---

## 🔍 Recommended Next Steps

### Phase 1: Quick Wins (1-2 weeks)
1. **Mastering Quality Detection** (pyloudnorm)
2. **Chord Progression Analysis** (basic-pitch)
3. **AI Lyric Critic** (Claude/GPT-4)
4. **Mastering Reference Comparison** (spectral diff)

**Rationale**: Immediate value, minimal dependencies, builds on existing infrastructure

### Phase 2: Vocal Isolation Foundation (2-3 weeks)
5. **Vocal Isolation** (Spleeter first, Demucs later)
6. **Vocal Performance Analysis** (pitch stability, breath control)
7. **Stem-Level Mixing Analysis** (vocal-to-instrumental ratio)

**Rationale**: Unlocks multiple downstream features, Spleeter is CPU-friendly

### Phase 3: Market Intelligence (3-4 weeks)
8. **TikTok Virality Predictor**
9. **Sync Licensing Matcher**
10. **Global Market Resonance** (expand existing Spotify/YouTube integration)

**Rationale**: Revenue-generating features, aligns with "Monetizer" tier

### Phase 4: Advanced ML (4-6 weeks)
11. **AI Cover Detection** (WavLM)
12. **Career Trajectory Modeling** (Prophet)
13. **Vocal Isolation Upgrade** (Demucs with GPU)

**Rationale**: Cutting-edge features, requires GPU infrastructure investment

---

## 💡 Key Insights

### Strengths to Leverage
1. **Modular Architecture**: Easy to add new services without breaking existing code
2. **JSONB Storage**: No schema migrations needed for new features
3. **Quality Metrics Framework**: Established 0-100 scoring convention
4. **ML Infrastructure**: PyTorch + Transformers already integrated

### Constraints to Address
1. **No GPU**: Limits heavy ML models (Demucs, WavLM)
2. **No Job Queue**: Long-running tasks block API responses
3. **Model Loading**: Each process loads models separately (memory inefficient)

### Strategic Recommendations
1. **Start with CPU-friendly features** (mastering quality, chord progressions)
2. **Invest in GPU infrastructure** before Phase 4 (AWS EC2 G4/G5 instances)
3. **Add job queue** (Celery + Redis) for vocal isolation and heavy ML tasks
4. **Implement model caching** (shared memory or model server)

---

## 📚 References

- **Current Stack**: `/home/dwood/tunescore/backend/pyproject.toml`
- **Audio Services**: `/home/dwood/tunescore/backend/app/services/audio/`
- **Database Schema**: `/home/dwood/tunescore/backend/app/models/track.py`
- **API Endpoints**: `/home/dwood/tunescore/backend/app/api/routers/tracks.py`

---

**Next Action**: Prioritize features using impact/effort scoring matrix

