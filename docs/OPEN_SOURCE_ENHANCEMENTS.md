# Open-Source Enhancements for TuneScore

## Priority 1: Critical Fixes (Week 1)

### 1. Add Essentia for Genre Classification
**Problem:** Misclassifying acoustic country as hip-hop/electronic
**Solution:** Use Essentia's pre-trained genre models

```python
# Download models
wget https://essentia.upf.edu/models/classification-heads/genre_discogs400/genre_discogs400-effnet-1.pb

# Integration
from essentia.standard import TensorflowPredictEffnetDiscogs

def detect_genre_essentia(audio_path):
    audio = MonoLoader(filename=audio_path, sampleRate=16000)()
    
    # Genre prediction
    genre_model = TensorflowPredictEffnetDiscogs(
        graphFilename='models/genre_discogs400-effnet-1.pb'
    )
    predictions = genre_model(audio)
    
    # Returns 400 genre probabilities
    return predictions
```

**Impact:** 
- Trained on 1M+ songs
- Can detect country, bluegrass, southern rock
- ~70-80% accuracy vs our current heuristics

---

### 2. Add Instrument Recognition
**Problem:** Can't distinguish fiddle from synthesizer
**Solution:** Use Essentia's instrument classifier OR source separation

#### Option A: Essentia Instrument Model
```python
from essentia.standard import TensorflowPredictMusiCNN

instrument_model = TensorflowPredictMusiCNN(
    graphFilename='models/instrument-recognition.pb'
)
instruments = instrument_model(audio)
# Returns: guitar, violin, drums, synth, etc.
```

#### Option B: Demucs + Spectral Analysis
```python
from demucs.separate import main as demucs_separate

# Separate sources
stems = demucs_separate(audio_path)
# → vocals, drums, bass, other

# Analyze "other" for acoustic instruments
other_track = stems['other']
spectral_features = analyze_spectral_characteristics(other_track)

if has_string_instrument_signature(spectral_features):
    acousticness += 0.5  # Boost for acoustic strings
```

**Impact:**
- Correctly identify acoustic vs electronic instrumentation
- Fix acousticness calculation
- Detect genre-defining instruments (fiddle = country/bluegrass)

---

## Priority 2: Better Audio Features (Week 2)

### 3. Improve Tempo Detection with Madmom
**Problem:** Complex rhythms (bluegrass) confuse librosa
**Solution:** Use madmom's DBN beat tracker

```python
from madmom.features import DBNDownBeatTrackingProcessor

proc = DBNDownBeatTrackingProcessor(fps=100)
beats = proc(audio_path)

# Detect tempo changes
tempos = detect_tempo_changes(beats)
avg_tempo = np.mean(tempos)
tempo_stability = 1.0 - np.std(tempos) / avg_tempo
```

**Impact:**
- Handle tempo variations (common in live recordings)
- Better beat tracking for syncopated rhythms
- Improve danceability calculation

---

### 4. Add Music Structure Analysis with MSAF
**Problem:** Missing verse/chorus/solo detection
**Solution:** Automatic section segmentation

```python
import msaf

# Analyze structure
boundaries, labels = msaf.process(audio_path, boundaries_id='sf')

sections = []
for i, (start, end) in enumerate(zip(boundaries[:-1], boundaries[1:])):
    sections.append({
        'type': labels[i],  # verse, chorus, bridge, solo
        'start': start,
        'end': end,
        'duration': end - start
    })

# Example output for "Devil Went Down to Georgia":
# [
#   {'type': 'intro', 'start': 0, 'end': 15},
#   {'type': 'verse', 'start': 15, 'end': 45},
#   {'type': 'chorus', 'start': 45, 'end': 60},
#   {'type': 'solo', 'start': 60, 'end': 120},  # Famous fiddle solo!
#   ...
# ]
```

**Impact:**
- Detect instrumental solos (key for rock/country/jazz)
- Better songwriting quality scoring
- Identify song structure patterns by genre

---

## Priority 3: Advanced Analysis (Week 3)

### 5. Add Chord Detection
**Problem:** No harmonic analysis
**Solution:** Use pychord or madmom chord recognition

```python
from madmom.features.chords import CNNChordFeatureProcessor

# Extract chord features
chord_processor = CNNChordFeatureProcessor()
chords = chord_processor(audio_path)

# Analyze progression
progressions = analyze_chord_progressions(chords)

# Country music signatures:
# - I-IV-V progressions
# - Simple chord changes
# - Major keys dominant
```

---

### 6. Melody/Scale Analysis with Aubio
**Problem:** No melodic analysis
**Solution:** Extract pitch contours and identify scales

```python
import aubio

# Pitch tracking
pitch_detector = aubio.pitch("default", 2048, 512, 44100)
pitches = []

for frame in audio_frames:
    pitch = pitch_detector(frame)[0]
    pitches.append(pitch)

# Detect scale type
scale = detect_scale(pitches)
# → 'major_pentatonic' (common in country)
# → 'blues_scale' (blues/rock)
# → 'phrygian' (metal, flamenco)
```

---

## Implementation Architecture

### New Service Structure
```
backend/app/services/
├── audio/
│   ├── feature_extraction.py (existing - librosa)
│   ├── essentia_features.py (NEW - genre, instruments)
│   ├── source_separation.py (NEW - demucs)
│   └── structure_analysis.py (NEW - msaf)
├── classification/
│   ├── genre_detector.py (existing - heuristics)
│   ├── genre_ml.py (NEW - ML models)
│   └── instrument_detector.py (NEW)
└── analysis/
    ├── harmony.py (NEW - chords, scales)
    ├── melody.py (NEW - pitch, contour)
    └── rhythm.py (NEW - better beat tracking)
```

### Hybrid Approach
```python
def detect_genre_hybrid(audio_path, lyrics):
    # 1. Get ML prediction (Essentia)
    ml_genres = essentia_genre_classifier(audio_path)  # 70% weight
    
    # 2. Get heuristic prediction (our current algorithm)
    features = extract_features(audio_path)
    heuristic_genres = genre_detector_heuristic(features, lyrics)  # 20% weight
    
    # 3. Get instrument-based hint
    instruments = detect_instruments(audio_path)  # 10% weight
    instrument_hint = map_instruments_to_genre(instruments)
    # fiddle → country/bluegrass
    # synthesizer → electronic
    # distorted_guitar → rock/metal
    
    # 4. Combine predictions
    final_genres = weighted_ensemble([ml_genres, heuristic_genres, instrument_hint])
    
    return final_genres
```

---

## Testing Plan

### Test Tracks by Genre
1. **Country:** "The Devil Went Down to Georgia" (Charlie Daniels Band)
2. **Hip-Hop:** "Get Your Freak On" (Missy Elliott) 
3. **Rock:** "Stairway to Heaven" (Led Zeppelin)
4. **Electronic:** "Levels" (Avicii)
5. **Jazz:** "Take Five" (Dave Brubeck)
6. **Classical:** Beethoven's 5th Symphony

### Expected Improvements
| Song | Current | Expected | Key Feature |
|------|---------|----------|-------------|
| Devil... | Hip-Hop (38%) | Country (75%) | Fiddle detection |
| Get Ur Freak On | Country (38%) | Hip-Hop (85%) | Already fixed! |
| Stairway... | ? | Rock (80%) | Guitar solo detection |

---

## Dependencies to Add

```toml
[tool.poetry.dependencies]
# ML-based audio analysis
essentia-tensorflow = "^2.1b6"
madmom = "^0.17.dev0"
demucs = "^4.0.0"

# Music theory & structure
music21 = "^9.1.0"
msaf = "^0.1.80"
aubio = "^0.4.9"

# Chord detection
pychord = "^0.5.5"

# Pre-trained models
transformers = "^4.30.0"
torch = "^2.0.0"
```

---

## Cost/Benefit Analysis

### Performance Impact
- **Essentia:** +500ms per track (acceptable)
- **Demucs:** +5-10s per track (run async, cache results)
- **MSAF:** +1-2s per track (acceptable)
- **Total:** ~10-15s per track (vs current ~5s)

### Accuracy Improvements
- **Genre classification:** 40% → 70-80% (2x improvement!)
- **Instrument detection:** 0% → 60-70% (NEW capability)
- **Structure analysis:** 0% → 70-80% (NEW capability)
- **Acousticness:** 60% → 85% (fixing electronic false positives)

### Storage Requirements
- **Pre-trained models:** ~500MB-1GB one-time download
- **Per-track cache:** +200MB (source-separated stems, optional)

---

## Migration Strategy

### Phase 1: Parallel Testing (Week 1)
- Add Essentia alongside existing system
- Log both predictions
- Compare results
- Don't change user-facing results yet

### Phase 2: Hybrid Ensemble (Week 2)
- Combine Essentia + heuristics
- Weight: 70% ML, 30% heuristics
- Deploy to production

### Phase 3: Full Features (Week 3-4)
- Add instrument detection
- Add structure analysis
- Add chord/melody analysis
- Update UI to show new features

---

## Success Metrics

✅ **"The Devil Went Down to Georgia"** classified as Country (not Hip-Hop)
✅ Acousticness > 70% for acoustic tracks
✅ Instrument detection working (fiddle, guitar, synth, etc.)
✅ Structure analysis detecting solos/verses/choruses
✅ Overall genre accuracy > 70%

---

## Resources

- **Essentia Documentation:** https://essentia.upf.edu/
- **Pre-trained Models:** https://essentia.upf.edu/models.html
- **Madmom:** https://madmom.readthedocs.io/
- **Demucs:** https://github.com/facebookresearch/demucs
- **MSAF:** https://github.com/urinieto/msaf
- **Music21:** https://web.mit.edu/music21/

