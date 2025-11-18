# TuneScore Competitive Features - Quick Start Guide

## 🚀 Installation

### 1. Install Core Dependencies

```bash
cd /home/dwood/tunescore/backend

# Install all dependencies via poetry
poetry install

# Or using venv pip
./venv/bin/pip install madmom demucs spacy langdetect deep-translator musicbrainzngs xgboost
```

### 2. Install Optional Dependencies

```bash
# spaCy English model (required for NER)
./venv/bin/python -m spacy download en_core_web_sm

# Essentia (optional, may require system dependencies)
# sudo apt-get install build-essential libyaml-dev libfftw3-dev libavcodec-dev libavformat-dev libavutil-dev libsamplerate0-dev libtag1-dev python3-dev python3-numpy-dev
# ./venv/bin/pip install essentia-tensorflow
```

### 3. Run Database Migration

```bash
cd /home/dwood/tunescore/backend
./venv/bin/alembic upgrade head
```

### 4. Set Environment Variables

Add to your `.env` file:

```bash
# Required for pitch generation
ANTHROPIC_API_KEY=your_anthropic_key_here

# Required for artist metrics
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

# Optional
YOUTUBE_API_KEY=your_youtube_key
```

## 🧪 Test Installation

```bash
cd /home/dwood/tunescore/backend
./venv/bin/python scripts/test_competitive_features.py
```

Expected output:
```
✓ All new models imported successfully
✓ Spectral analyzer works
✓ Hook detector finds viral segments
✓ Theme extractor loads model
✓ Mood classifier generates tags
```

## 💻 Usage Examples

### 1. Advanced Audio Analysis

```python
from app.services.audio.spectral_advanced import AdvancedSpectralAnalyzer
from app.services.audio.hook_detector_advanced import ViralHookDetector

# Spectral analysis
analyzer = AdvancedSpectralAnalyzer()
features = analyzer.analyze("path/to/audio.mp3")

print(f"BPM: {features['rhythm']['bpm']}")
print(f"Key: {features['tonal']['key']}")
print(f"Spectral complexity: {features['spectral']['complexity_mean']}")

# Viral hook detection
detector = ViralHookDetector()
segments = detector.detect_viral_segments("path/to/audio.mp3", segment_duration=15.0)

for segment in segments['viral_segments'][:3]:
    print(f"Segment {segment['start_time']}-{segment['end_time']}s: Score {segment['score']}")
    print(f"  Reasons: {', '.join(segment['reasons'])}")
```

### 2. NLP & Theme Extraction

```python
from app.services.lyrics.multilingual_analyzer import MultilingualAnalyzer
from app.services.lyrics.theme_extractor import ThemeExtractor

# Multilingual analysis
analyzer = MultilingualAnalyzer()
result = analyzer.analyze("Te amo más de lo que puedo decir")

print(f"Language: {result['language']}")
if result['was_translated']:
    print(f"Translation: {result['translation']}")

# Theme extraction
extractor = ThemeExtractor()
themes = extractor.extract_themes(lyrics_text, top_n=5)

for theme, score in themes['themes'].items():
    print(f"{theme}: {score}")
```

### 3. AI Tagging & Pitch Generation

```python
from app.services.ai_tagging.mood_classifier import MoodClassifier
from app.services.ai_tagging.pitch_generator import PitchGenerator

# Mood classification
classifier = MoodClassifier()
moods = classifier.classify(sonic_genome, lyrical_genome)

print(f"Primary mood: {moods['primary_mood']}")
print(f"All moods: {', '.join(moods['moods'])}")

# Commercial tags
tags = classifier.classify_commercial_tags(sonic_genome)
print(f"Commercial tags: {', '.join(tags)}")

# Pitch generation (requires ANTHROPIC_API_KEY)
generator = PitchGenerator()
pitch = generator.generate_pitch(
    track_title="Sunset Dreams",
    artist_name="Indie Artist",
    sonic_genome=sonic_genome,
    lyrical_genome=lyrical_genome,
    tags={"moods": moods['moods'], "commercial_tags": tags}
)

print(f"Elevator pitch: {pitch['elevator_pitch']}")
print(f"Cost: ${pitch['cost']:.4f}")
```

### 4. Artist Intelligence

```python
from app.services.artist_intelligence.snapshot_collector import ArtistSnapshotCollector
from app.core.database import AsyncSessionLocal

# Collect artist snapshots
collector = ArtistSnapshotCollector()

async with AsyncSessionLocal() as db:
    # Collect all platform snapshots
    snapshots = await collector.collect_all_snapshots(artist_id=1, db=db)
    
    # Get metrics history
    history = await collector.get_metrics_history(
        artist_id=1,
        platform="spotify",
        days=90,
        db=db
    )
    
    for snapshot in history:
        print(f"{snapshot['date']}: {snapshot['metrics']['followers']} followers")
```

### 5. Catalog Valuation

```python
from app.services.catalog.credits_fetcher import CreditsFetcher
from app.services.catalog.valuator import CatalogValuator

# Fetch credits from MusicBrainz
fetcher = CreditsFetcher()
credits = fetcher.get_credits_by_search("Bohemian Rhapsody", "Queen")

if credits['found']:
    print(f"Match score: {credits['match_score']}")
    for credit in credits['credits']:
        print(f"  {credit['name']} - {credit['role']}")

# Catalog valuation
valuator = CatalogValuator()
tracks = [
    {
        "monthly_streams": 100000,
        "tunescore": 85,
        "genre": "pop",
        "commercial_tags": ["sync-ready", "radio-friendly"]
    },
    # ... more tracks
]

valuation = valuator.calculate_valuation(tracks)

print(f"Estimated value: ${valuation['estimated_value']:,.2f}")
print(f"Annual revenue: ${valuation['annual_revenue']:,.2f}")
print(f"Valuation multiple: {valuation['valuation_multiple']}x")
print(f"Confidence: {valuation['confidence']}")
```

## 🔌 Integration into Existing Analysis Pipeline

### Extend Track Analysis

```python
# In your existing track analysis workflow:

from app.services.audio.spectral_advanced import AdvancedSpectralAnalyzer
from app.services.audio.hook_detector_advanced import ViralHookDetector
from app.services.lyrics.multilingual_analyzer import MultilingualAnalyzer
from app.services.lyrics.theme_extractor import ThemeExtractor
from app.services.ai_tagging.mood_classifier import MoodClassifier

async def analyze_track_enhanced(track_id: int, audio_path: str, lyrics: str):
    """Enhanced track analysis with competitive features."""
    
    # Get existing sonic/lyrical genome
    extractor = AudioFeatureExtractor()
    sonic_genome = extractor.extract_sonic_genome(audio_path)
    
    # Add advanced spectral features
    spectral_analyzer = AdvancedSpectralAnalyzer()
    essentia_features = spectral_analyzer.analyze(audio_path)
    sonic_genome["essentia_features"] = essentia_features
    
    # Detect viral hooks
    hook_detector = ViralHookDetector()
    viral_segments = hook_detector.detect_viral_segments(audio_path)
    hook_data = {"viral_segments": viral_segments['viral_segments']}
    
    # Multilingual analysis
    ml_analyzer = MultilingualAnalyzer()
    ml_analysis = ml_analyzer.analyze(lyrics)
    
    # Theme extraction
    theme_extractor = ThemeExtractor()
    themes = theme_extractor.extract_themes(lyrics)
    
    # Create lyrical genome
    lyrical_genome = {
        "language": ml_analysis["language"],
        "translation": ml_analysis.get("translation"),
        "entities": ml_analysis.get("entities", []),
        "themes_advanced": themes.get("themes", {}),
        "linguistic_features": ml_analysis.get("linguistic_features", {})
    }
    
    # Generate mood tags
    mood_classifier = MoodClassifier()
    moods = mood_classifier.classify(sonic_genome, lyrical_genome)
    commercial_tags = mood_classifier.classify_commercial_tags(sonic_genome)
    
    # Store in database
    analysis = Analysis(
        track_id=track_id,
        sonic_genome=sonic_genome,
        lyrical_genome=lyrical_genome,
        hook_data=hook_data
    )
    
    track_tags = TrackTags(
        track_id=track_id,
        moods=moods['moods'],
        commercial_tags=commercial_tags
    )
    
    # Save to DB
    db.add(analysis)
    db.add(track_tags)
    await db.commit()
    
    return {
        "sonic_genome": sonic_genome,
        "lyrical_genome": lyrical_genome,
        "hook_data": hook_data,
        "moods": moods,
        "commercial_tags": commercial_tags
    }
```

## 📊 Data Flow

```
Upload Track
    ↓
Audio Analysis
    ├─ Basic Features (librosa) → sonic_genome
    ├─ Advanced Spectral (essentia) → sonic_genome.essentia_features
    ├─ Stem Separation (demucs) → sonic_genome.stem_features
    └─ Viral Hooks (madmom) → hook_data.viral_segments
    ↓
Lyrics Analysis
    ├─ Language Detection → lyrical_genome.language
    ├─ Translation → lyrical_genome.translation
    ├─ NER (spaCy) → lyrical_genome.entities
    └─ Themes (BART) → lyrical_genome.themes_advanced
    ↓
AI Tagging
    ├─ Mood Classification → track_tags.moods
    ├─ Commercial Tags → track_tags.commercial_tags
    └─ Pitch Generation (Claude) → pitch_copy.*
    ↓
Store in Database (JSONB)
```

## 🎯 Feature Availability Matrix

| Feature | Free/Local | Paid API | Optional Dep |
|---------|------------|----------|--------------|
| Advanced Spectral | ✅ librosa | ⚠️ essentia | essentia |
| Stem Separation | ❌ | ❌ | demucs |
| Viral Hooks | ✅ librosa | ⚠️ madmom | madmom |
| Language Detection | ❌ | ❌ | langdetect |
| Translation | ✅ Google | ⚠️ deepl | deep-translator |
| NER | ❌ | ❌ | spacy |
| Theme Extraction | ✅ BART | ❌ | transformers |
| Mood Classification | ✅ Rules | ❌ | - |
| Pitch Generation | ❌ | ✅ Claude | anthropic |
| Credits Fetch | ✅ MusicBrainz | ❌ | musicbrainzngs |

## 🛠️ Troubleshooting

### "Module not found" errors
```bash
# Ensure venv is activated or use full path
./venv/bin/python your_script.py
```

### Essentia installation fails
```bash
# Essentia is optional - features work with librosa fallback
# Skip if installation is problematic
```

### Theme extraction slow on first run
```bash
# First run downloads BART model (~500MB)
# Subsequent runs are fast (model cached)
```

### Pitch generation "API key not set"
```bash
# Add to .env:
echo "ANTHROPIC_API_KEY=your_key" >> .env
```

## 📚 Next Steps

1. Review `COMPETITIVE_FEATURES_SUMMARY.md` for architecture details
2. Check `IMPLEMENTATION_PROGRESS.md` for completion status
3. Run tests: `./venv/bin/python scripts/test_competitive_features.py`
4. Review API endpoints (when implemented)
5. Check frontend routes (when implemented)

---

**Questions?** Check the inline documentation in each service module.  
**Issues?** All code includes comprehensive error handling and logging.

