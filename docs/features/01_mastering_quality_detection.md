# Feature Brief: Mastering Quality Detection

**Priority**: 4.0 (Highest)  
**Phase**: 1 (Quick Wins)  
**Effort**: 2/10 (1-2 days)  
**Impact**: 8/10

---

## 🎯 Overview

Analyze audio mastering quality using industry-standard LUFS (Loudness Units Full Scale) measurement and Dynamic Range (DR) metering. Provide instant feedback on whether tracks meet streaming platform loudness targets and detect over-compression ("loudness war").

---

## 👥 User Stories

### Creator Tier
- "Is my track loud enough for Spotify?" → Check LUFS against -14 LUFS target
- "Am I over-compressing my mix?" → DR score flags over-compression
- "How does my mastering compare to professional tracks?" → Grade + recommendations

### Developer Tier
- "Which demos have professional mastering?" → Filter by mastering quality grade
- "Identify tracks that need remastering" → Flag tracks below quality threshold

### Monetizer Tier
- "Assess catalog mastering quality" → Bulk analysis of catalog
- "Prioritize remastering budget" → Sort by quality score

---

## 🏗️ Architecture

### Data Flow
```
1. User uploads track → Audio file stored in /files/{user_id}/{track_id}/
2. Track analysis triggered → AudioFeatureExtractor.load_audio()
3. Mastering analysis runs → MasteringAnalyzer.analyze()
   ├── LUFS measurement (pyloudnorm)
   ├── Peak/RMS ratio calculation
   ├── Dynamic Range (DR) score
   └── Platform target comparison
4. Results stored → analyses.mastering_quality (JSONB)
5. Frontend displays → MasteringQualityCard.svelte
```

### Service Layer
```python
# backend/app/services/audio/mastering_analyzer.py

import pyloudnorm as pyln
import numpy as np
import librosa

class MasteringAnalyzer:
    """Analyze mastering quality using LUFS and DR metering."""
    
    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate
        self.meter = pyln.Meter(sample_rate)  # BS.1770 meter
    
    def analyze(self, audio_path: str) -> dict:
        """
        Analyze mastering quality.
        
        Returns:
            {
                "lufs": -12.5,
                "lufs_grade": "Too Loud",
                "peak_db": -0.3,
                "rms_db": -18.2,
                "dynamic_range": 8.5,
                "dr_grade": "Acceptable",
                "platform_targets": {
                    "spotify": {"target": -14, "delta": +1.5, "status": "too_loud"},
                    "apple_music": {"target": -16, "delta": +3.5, "status": "too_loud"},
                    "youtube": {"target": -13, "delta": +0.5, "status": "optimal"},
                    "tidal": {"target": -14, "delta": +1.5, "status": "too_loud"}
                },
                "overall_quality": 72,
                "quality_grade": "Good",
                "recommendations": [...]
            }
        """
        y, sr = librosa.load(audio_path, sr=self.sample_rate, mono=True)
        
        # 1. LUFS measurement (integrated loudness)
        lufs = self.meter.integrated_loudness(y)
        
        # 2. Peak level (dBFS)
        peak_db = 20 * np.log10(np.max(np.abs(y)))
        
        # 3. RMS level (dBFS)
        rms = np.sqrt(np.mean(y**2))
        rms_db = 20 * np.log10(rms + 1e-8)
        
        # 4. Dynamic Range (DR) score
        # DR = (Peak - RMS) in dB, averaged over segments
        dynamic_range = self._calculate_dr_score(y)
        
        # 5. Platform target comparison
        platform_targets = self._compare_platform_targets(lufs)
        
        # 6. Overall quality score (0-100)
        overall_quality = self._calculate_quality_score(
            lufs, peak_db, dynamic_range
        )
        
        # 7. Recommendations
        recommendations = self._generate_recommendations(
            lufs, peak_db, dynamic_range, platform_targets
        )
        
        return {
            "lufs": round(lufs, 1),
            "lufs_grade": self._get_lufs_grade(lufs),
            "peak_db": round(peak_db, 1),
            "rms_db": round(rms_db, 1),
            "dynamic_range": round(dynamic_range, 1),
            "dr_grade": self._get_dr_grade(dynamic_range),
            "platform_targets": platform_targets,
            "overall_quality": round(overall_quality, 1),
            "quality_grade": self._get_quality_grade(overall_quality),
            "recommendations": recommendations,
        }
    
    def _calculate_dr_score(self, y: np.ndarray) -> float:
        """Calculate Dynamic Range score (DR meter standard)."""
        # Split into 3-second segments
        segment_length = self.sample_rate * 3
        segments = [
            y[i:i+segment_length] 
            for i in range(0, len(y), segment_length)
            if len(y[i:i+segment_length]) == segment_length
        ]
        
        if not segments:
            return 0.0
        
        # Calculate DR for each segment
        dr_values = []
        for segment in segments:
            peak = np.max(np.abs(segment))
            rms = np.sqrt(np.mean(segment**2))
            if rms > 0:
                dr = 20 * np.log10(peak / rms)
                dr_values.append(dr)
        
        # Return median DR (robust to outliers)
        return float(np.median(dr_values)) if dr_values else 0.0
    
    def _compare_platform_targets(self, lufs: float) -> dict:
        """Compare LUFS to streaming platform targets."""
        targets = {
            "spotify": -14,
            "apple_music": -16,
            "youtube": -13,
            "tidal": -14,
            "soundcloud": -10,
        }
        
        results = {}
        for platform, target in targets.items():
            delta = lufs - target
            
            if abs(delta) <= 1:
                status = "optimal"
            elif delta > 1:
                status = "too_loud"
            else:
                status = "too_quiet"
            
            results[platform] = {
                "target": target,
                "delta": round(delta, 1),
                "status": status,
            }
        
        return results
    
    def _calculate_quality_score(
        self, lufs: float, peak_db: float, dr: float
    ) -> float:
        """Calculate overall mastering quality score (0-100)."""
        # 1. LUFS score (optimal: -14 to -10 LUFS)
        if -14 <= lufs <= -10:
            lufs_score = 100
        elif -16 <= lufs < -14:
            lufs_score = 80 + (lufs + 16) * 10
        elif -10 < lufs <= -8:
            lufs_score = 80 + (10 - lufs) * 10
        elif -20 <= lufs < -16:
            lufs_score = 60 + (lufs + 20) * 5
        else:
            lufs_score = 40
        
        # 2. Peak score (optimal: -0.5 to -0.1 dBFS)
        if -0.5 <= peak_db <= -0.1:
            peak_score = 100
        elif -1.0 <= peak_db < -0.5:
            peak_score = 80
        elif peak_db > -0.1:
            peak_score = 50  # Clipping risk
        else:
            peak_score = 60  # Too much headroom
        
        # 3. DR score (optimal: 8-14 DR)
        if 8 <= dr <= 14:
            dr_score = 100
        elif 6 <= dr < 8:
            dr_score = 70  # Over-compressed
        elif 14 < dr <= 18:
            dr_score = 80  # Natural dynamics
        elif dr < 6:
            dr_score = 40  # Severely over-compressed (loudness war)
        else:
            dr_score = 60  # Too dynamic (under-compressed)
        
        # Weighted average
        return (lufs_score * 0.4) + (peak_score * 0.3) + (dr_score * 0.3)
    
    def _get_lufs_grade(self, lufs: float) -> str:
        """Convert LUFS to grade."""
        if -14 <= lufs <= -10:
            return "Optimal"
        elif -16 <= lufs < -14:
            return "Slightly Quiet"
        elif -10 < lufs <= -8:
            return "Slightly Loud"
        elif lufs < -16:
            return "Too Quiet"
        else:
            return "Too Loud"
    
    def _get_dr_grade(self, dr: float) -> str:
        """Convert DR to grade."""
        if dr >= 14:
            return "Excellent Dynamics"
        elif dr >= 10:
            return "Good Dynamics"
        elif dr >= 8:
            return "Acceptable"
        elif dr >= 6:
            return "Over-Compressed"
        else:
            return "Severely Over-Compressed"
    
    def _get_quality_grade(self, score: float) -> str:
        """Convert quality score to grade."""
        if score >= 90:
            return "Professional"
        elif score >= 75:
            return "Good"
        elif score >= 60:
            return "Acceptable"
        elif score >= 45:
            return "Needs Improvement"
        else:
            return "Poor"
    
    def _generate_recommendations(
        self, lufs: float, peak_db: float, dr: float, platform_targets: dict
    ) -> list[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # LUFS recommendations
        if lufs < -16:
            recommendations.append(
                "Track is too quiet. Apply makeup gain or use a limiter to increase loudness."
            )
        elif lufs > -8:
            recommendations.append(
                "Track is too loud. Reduce limiting/compression to avoid distortion."
            )
        
        # Peak recommendations
        if peak_db > -0.1:
            recommendations.append(
                "Peak level is too high (clipping risk). Leave at least -0.3 dBFS headroom."
            )
        elif peak_db < -2.0:
            recommendations.append(
                "Peak level is too low. You have excessive headroom—increase output level."
            )
        
        # DR recommendations
        if dr < 6:
            recommendations.append(
                "Dynamic range is too low (loudness war territory). Reduce compression/limiting."
            )
        elif dr > 18:
            recommendations.append(
                "Dynamic range is very high. Consider gentle compression for streaming."
            )
        
        # Platform-specific recommendations
        spotify_status = platform_targets["spotify"]["status"]
        if spotify_status == "too_loud":
            recommendations.append(
                "Spotify will turn down your track. Target -14 LUFS for optimal loudness."
            )
        elif spotify_status == "too_quiet":
            recommendations.append(
                "Spotify will turn up your track (adding noise). Increase loudness to -14 LUFS."
            )
        
        return recommendations
```

---

## 🗄️ Database Schema

### Update `analyses` table (JSONB field)
```python
# backend/app/models/track.py

class Analysis(Base):
    # ... existing fields ...
    mastering_quality = Column(JSONB, nullable=True)  # NEW FIELD
```

### Migration
```bash
alembic revision -m "add_mastering_quality_to_analyses"
```

```python
# alembic/versions/xxx_add_mastering_quality_to_analyses.py

def upgrade():
    op.add_column('analyses', sa.Column('mastering_quality', JSONB, nullable=True))

def downgrade():
    op.drop_column('analyses', 'mastering_quality')
```

---

## 🌐 API Endpoints

### Update existing track analysis endpoint
```python
# backend/app/api/routers/tracks.py

@router.get("/tracks/{track_id}/analysis")
async def get_track_analysis(track_id: int, db: AsyncSession = Depends(get_db)):
    """Get track analysis including mastering quality."""
    # ... existing code ...
    
    # Add mastering quality to response
    if analysis.mastering_quality:
        response["mastering_quality"] = analysis.mastering_quality
    
    return response
```

### Add mastering quality to track upload flow
```python
# backend/app/services/audio/feature_extraction.py

def extract_audio_features(audio_path: str):
    # ... existing code ...
    
    # Add mastering analysis
    mastering_analyzer = MasteringAnalyzer()
    mastering_quality = mastering_analyzer.analyze(audio_path)
    
    return sonic_genome, hook_data, quality_metrics, mastering_quality
```

---

## 🎨 Frontend Components

### MasteringQualityCard.svelte
```svelte
<script lang="ts">
  import { Card, Badge, ProgressBar } from '$lib/components/ui';
  
  export let masteringQuality: {
    lufs: number;
    lufs_grade: string;
    peak_db: number;
    dynamic_range: number;
    dr_grade: string;
    platform_targets: Record<string, any>;
    overall_quality: number;
    quality_grade: string;
    recommendations: string[];
  };
  
  function getGradeColor(grade: string) {
    if (grade.includes('Professional') || grade.includes('Optimal')) return 'green';
    if (grade.includes('Good') || grade.includes('Acceptable')) return 'blue';
    if (grade.includes('Needs Improvement')) return 'yellow';
    return 'red';
  }
</script>

<Card title="Mastering Quality">
  <div class="space-y-4">
    <!-- Overall Quality -->
    <div>
      <div class="flex justify-between mb-2">
        <span class="font-semibold">Overall Quality</span>
        <Badge color={getGradeColor(masteringQuality.quality_grade)}>
          {masteringQuality.quality_grade}
        </Badge>
      </div>
      <ProgressBar value={masteringQuality.overall_quality} max={100} />
    </div>
    
    <!-- LUFS -->
    <div>
      <div class="flex justify-between">
        <span>Loudness (LUFS)</span>
        <span class="font-mono">{masteringQuality.lufs} LUFS</span>
      </div>
      <Badge color={getGradeColor(masteringQuality.lufs_grade)}>
        {masteringQuality.lufs_grade}
      </Badge>
    </div>
    
    <!-- Dynamic Range -->
    <div>
      <div class="flex justify-between">
        <span>Dynamic Range</span>
        <span class="font-mono">{masteringQuality.dynamic_range} DR</span>
      </div>
      <Badge color={getGradeColor(masteringQuality.dr_grade)}>
        {masteringQuality.dr_grade}
      </Badge>
    </div>
    
    <!-- Platform Targets -->
    <div>
      <h4 class="font-semibold mb-2">Platform Targets</h4>
      <div class="grid grid-cols-2 gap-2">
        {#each Object.entries(masteringQuality.platform_targets) as [platform, data]}
          <div class="flex items-center justify-between p-2 bg-gray-50 rounded">
            <span class="capitalize">{platform.replace('_', ' ')}</span>
            <span class="text-sm" class:text-green-600={data.status === 'optimal'}
                                   class:text-red-600={data.status !== 'optimal'}>
              {data.delta > 0 ? '+' : ''}{data.delta} dB
            </span>
          </div>
        {/each}
      </div>
    </div>
    
    <!-- Recommendations -->
    {#if masteringQuality.recommendations.length > 0}
      <div>
        <h4 class="font-semibold mb-2">Recommendations</h4>
        <ul class="list-disc list-inside space-y-1 text-sm">
          {#each masteringQuality.recommendations as rec}
            <li>{rec}</li>
          {/each}
        </ul>
      </div>
    {/if}
  </div>
</Card>
```

---

## 📦 Dependencies

### New Dependencies
```toml
# backend/pyproject.toml
pyloudnorm = "^0.1.1"  # LUFS measurement (BS.1770)
```

### Installation
```bash
cd /home/dwood/tunescore/backend
source venv/bin/activate
poetry add pyloudnorm
```

---

## ✅ Testing Strategy

### Unit Tests
```python
# backend/app/tests/test_mastering_analyzer.py

import pytest
from app.services.audio.mastering_analyzer import MasteringAnalyzer

def test_analyze_professional_track():
    analyzer = MasteringAnalyzer()
    result = analyzer.analyze("test_files/professional_master.wav")
    
    assert -16 <= result["lufs"] <= -8
    assert result["dynamic_range"] >= 6
    assert result["overall_quality"] >= 60

def test_analyze_overcompressed_track():
    analyzer = MasteringAnalyzer()
    result = analyzer.analyze("test_files/overcompressed.wav")
    
    assert result["dynamic_range"] < 6
    assert "over-compressed" in result["dr_grade"].lower()
    assert any("compression" in rec.lower() for rec in result["recommendations"])
```

### Integration Tests
```python
def test_track_upload_includes_mastering_quality(client, auth_headers):
    # Upload track
    response = client.post(
        "/api/v1/tracks/upload",
        files={"audio": open("test_files/track.mp3", "rb")},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    track_id = response.json()["id"]
    
    # Get analysis
    analysis = client.get(f"/api/v1/tracks/{track_id}/analysis", headers=auth_headers)
    
    assert "mastering_quality" in analysis.json()
    assert "lufs" in analysis.json()["mastering_quality"]
```

---

## 📊 Success Metrics

### Technical Metrics
- Analysis time: <2 seconds per track
- Accuracy: LUFS within ±0.5 dB of reference meters (iZotope Insight, Waves WLM)
- Coverage: 100% of uploaded tracks analyzed

### User Metrics
- Feature usage: >50% of Creator tier users view mastering quality
- Engagement: Average time on mastering quality card >30 seconds
- Actionability: >30% of users re-upload tracks after seeing recommendations

### Business Metrics
- Conversion: 10% increase in Creator tier upgrades
- Retention: 5% increase in Creator tier retention
- NPS: +5 point increase for Creator tier users

---

## 🚀 Implementation Timeline

### Day 1: Backend Development
- [ ] Create `MasteringAnalyzer` class
- [ ] Implement LUFS measurement
- [ ] Implement DR calculation
- [ ] Add platform target comparison
- [ ] Write unit tests

### Day 2: Integration & Frontend
- [ ] Add mastering quality to track analysis flow
- [ ] Create database migration
- [ ] Update API endpoints
- [ ] Create `MasteringQualityCard.svelte`
- [ ] Write integration tests
- [ ] Deploy to staging

---

## 🔒 Security & Performance

### Performance Considerations
- LUFS calculation is CPU-intensive (~1-2 seconds per track)
- Run asynchronously to avoid blocking API responses
- Cache results in database (no need to recalculate)

### Security Considerations
- No new security risks (uses existing audio file upload flow)
- Validate audio file format before analysis
- Rate limit analysis requests (prevent abuse)

---

## 📚 References

- **ITU-R BS.1770**: International standard for loudness measurement
- **pyloudnorm**: https://github.com/csteinmetz1/pyloudnorm
- **Dynamic Range Database**: http://dr.loudness-war.info/
- **Spotify Loudness Normalization**: https://artists.spotify.com/en/help/article/loudness-normalization

