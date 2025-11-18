# Feature Brief: Vocal Isolation (Spleeter)

**Priority**: 2.25  
**Phase**: 2 (Vocal Intelligence)  
**Effort**: 4/10 (3-5 days)  
**Impact**: 9/10

---

## 🎯 Overview

Use Spleeter (Deezer's open-source model) to separate vocals from accompaniment. Enables downstream features: vocal performance analysis, stem-level mixing analysis, and vocal effects detection.

---

## 👥 User Stories

- Creator: "Isolate vocals for remix/sampling"
- Creator: "Analyze my vocal performance separately"
- Developer: "Compare vocal production quality across demos"
- Monetizer: "Assess vocal clarity for sync licensing"

---

## 🏗️ Architecture

```python
# backend/app/services/audio/vocal_separator.py

from spleeter.separator import Separator
import os

class VocalSeparator:
    """Separate vocals using Spleeter."""
    
    def __init__(self):
        # Use 2-stem model (vocals + accompaniment)
        self.separator = Separator('spleeter:2stems')
    
    def separate(self, audio_path: str, output_dir: str) -> dict:
        """
        Separate vocals from accompaniment.
        
        Returns:
            {
                "vocals_path": "/files/1/10/vocals.wav",
                "accompaniment_path": "/files/1/10/accompaniment.wav",
                "vocal_to_instrumental_ratio": 0.65,
                "vocal_clarity_score": 82
            }
        """
        # Separate stems
        self.separator.separate_to_file(audio_path, output_dir)
        
        # Paths to separated stems
        vocals_path = os.path.join(output_dir, "vocals.wav")
        accompaniment_path = os.path.join(output_dir, "accompaniment.wav")
        
        # Analyze vocal-to-instrumental ratio
        ratio = self._calculate_vocal_ratio(vocals_path, accompaniment_path)
        
        # Vocal clarity score
        clarity = self._calculate_vocal_clarity(vocals_path)
        
        return {
            "vocals_path": vocals_path,
            "accompaniment_path": accompaniment_path,
            "vocal_to_instrumental_ratio": round(ratio, 2),
            "vocal_clarity_score": round(clarity, 1)
        }
    
    def _calculate_vocal_ratio(self, vocals_path: str, accompaniment_path: str) -> float:
        """Calculate vocal-to-instrumental energy ratio."""
        import librosa
        import numpy as np
        
        y_vocals, _ = librosa.load(vocals_path, sr=22050)
        y_accompaniment, _ = librosa.load(accompaniment_path, sr=22050)
        
        vocal_energy = np.sum(y_vocals ** 2)
        accompaniment_energy = np.sum(y_accompaniment ** 2)
        
        if accompaniment_energy == 0:
            return 1.0
        
        return vocal_energy / (vocal_energy + accompaniment_energy)
    
    def _calculate_vocal_clarity(self, vocals_path: str) -> float:
        """Calculate vocal clarity score (0-100)."""
        import librosa
        import numpy as np
        
        y, sr = librosa.load(vocals_path, sr=22050)
        
        # Spectral clarity (high spectral centroid = clear vocals)
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        clarity_score = np.mean(spectral_centroid) / 40  # Normalize
        
        return min(clarity_score, 100)
```

---

## 🗄️ Database Schema

```python
class Analysis(Base):
    # ... existing fields ...
    vocal_separation = Column(JSONB, nullable=True)  # NEW FIELD
    # Stores: vocals_path, accompaniment_path, ratios, clarity
```

---

## 📦 Dependencies

```toml
# backend/pyproject.toml
spleeter = "^2.3.2"  # Deezer's vocal separation
tensorflow = "^2.13.0"  # Required by Spleeter
```

**Note**: Spleeter is CPU-friendly (no GPU required)

---

## 🚀 Implementation Timeline

**Day 1-2**: Spleeter integration, stem separation  
**Day 3**: Vocal analysis (ratio, clarity)  
**Day 4**: API endpoints, database migration  
**Day 5**: Frontend component, testing

---

## 📊 Success Metrics

- Separation time: <30 seconds per track (CPU)
- Quality: Vocal clarity score >70 for professional tracks
- Usage: >25% of Creator tier users separate vocals

