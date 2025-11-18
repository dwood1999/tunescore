# TuneScore: Feature Technical Briefs

This directory contains detailed technical briefs for advanced audio analysis features.

---

## 📋 Feature Briefs

### Phase 1: Quick Wins (Weeks 1-2)

1. **[Mastering Quality Detection](01_mastering_quality_detection.md)** - Priority: 4.0
   - LUFS measurement, Dynamic Range scoring, platform target comparison
   - Dependencies: `pyloudnorm`
   - Effort: 1-2 days

2. **[Chord Progression Analysis](02_chord_progression_analysis.md)** - Priority: 3.0
   - MIDI extraction, chord detection, harmonic complexity scoring
   - Dependencies: `basic-pitch` (Spotify's model)
   - Effort: 2-3 days

3. **[AI Lyric Critic](03_ai_lyric_critic.md)** - Priority: 2.7
   - Claude/GPT-4 powered feedback, rewrite suggestions, rhyme improvements
   - Dependencies: Already installed (anthropic, openai)
   - Effort: 1-2 days

### Phase 2: Vocal Intelligence (Weeks 3-5)

4. **[Vocal Isolation (Spleeter)](04_vocal_isolation_spleeter.md)** - Priority: 2.25
   - Vocal/accompaniment separation, vocal clarity scoring
   - Dependencies: `spleeter`, `tensorflow`
   - Effort: 3-5 days

5. **[TikTok Virality Predictor](05_tiktok_virality_predictor.md)** - Priority: 2.25
   - Segment analysis, quotability scoring, loop potential
   - Dependencies: None (extends existing features)
   - Effort: 3-4 days

---

## 🎯 Implementation Order

### Recommended Sequence

**Week 1:**
- Day 1-2: Mastering Quality Detection
- Day 3-5: Chord Progression Analysis

**Week 2:**
- Day 1-2: AI Lyric Critic
- Day 3-5: Testing, bug fixes, documentation

**Week 3-4:**
- Day 1-5: Vocal Isolation (Spleeter)
- Day 6-8: Vocal Performance Analysis (downstream feature)

**Week 5:**
- Day 1-4: TikTok Virality Predictor
- Day 5: Integration testing, deployment

---

## 📊 Feature Comparison

| Feature | Priority | Effort | Impact | Dependencies | GPU Required |
|---------|----------|--------|--------|--------------|--------------|
| Mastering Quality | 4.0 | 2/10 | 8/10 | pyloudnorm | No |
| Chord Progression | 3.0 | 3/10 | 9/10 | basic-pitch | No |
| AI Lyric Critic | 2.7 | 3/10 | 8/10 | None (installed) | No (API) |
| Vocal Isolation | 2.25 | 4/10 | 9/10 | spleeter | No |
| TikTok Virality | 2.25 | 4/10 | 9/10 | None | No |

---

## 🏗️ Common Architecture Patterns

### Service Layer Pattern
All features follow the same service layer pattern:

```python
# backend/app/services/{category}/{feature}_analyzer.py

class FeatureAnalyzer:
    """Analyze {feature}."""
    
    def __init__(self):
        # Initialize models, load configs
        pass
    
    def analyze(self, audio_path: str, **kwargs) -> dict:
        """
        Analyze {feature}.
        
        Returns:
            {
                "metric_1": value,
                "metric_2": value,
                "score": 0-100,
                "grade": "A-F",
                "recommendations": [...]
            }
        """
        # 1. Load audio
        # 2. Extract features
        # 3. Calculate scores
        # 4. Generate recommendations
        return results
```

### Database Storage Pattern
All features store results in JSONB fields:

```python
# backend/app/models/track.py

class Analysis(Base):
    # ... existing fields ...
    feature_name = Column(JSONB, nullable=True)
```

**Benefits:**
- No schema migrations for new metrics
- Flexible data structure evolution
- Zero-transform principle (store raw AI outputs)

### API Endpoint Pattern
All features expose consistent API endpoints:

```python
# backend/app/api/routers/tracks.py

@router.get("/tracks/{track_id}/analysis")
async def get_track_analysis(track_id: int):
    """Get full track analysis including all features."""
    # Returns all JSONB fields in one response
    pass
```

### Frontend Component Pattern
All features use consistent Svelte components:

```svelte
<!-- frontend/src/lib/components/{Feature}Card.svelte -->

<script lang="ts">
  import { Card, Badge, ProgressBar } from '$lib/components/ui';
  export let featureData: FeatureType;
</script>

<Card title="{Feature Name}">
  <!-- Score/Grade -->
  <!-- Metrics -->
  <!-- Recommendations -->
</Card>
```

---

## 🧪 Testing Strategy

### Unit Tests
Each feature includes unit tests:

```python
# backend/app/tests/test_{feature}_analyzer.py

def test_analyze_professional_track():
    analyzer = FeatureAnalyzer()
    result = analyzer.analyze("test_files/professional.wav")
    assert result["score"] >= 70

def test_analyze_amateur_track():
    analyzer = FeatureAnalyzer()
    result = analyzer.analyze("test_files/amateur.wav")
    assert result["score"] < 70
```

### Integration Tests
Test full upload → analysis → API flow:

```python
def test_track_upload_includes_feature(client, auth_headers):
    response = client.post(
        "/api/v1/tracks/upload",
        files={"audio": open("test.mp3", "rb")},
        headers=auth_headers
    )
    track_id = response.json()["id"]
    
    analysis = client.get(f"/api/v1/tracks/{track_id}/analysis")
    assert "feature_name" in analysis.json()
```

---

## 📊 Success Metrics

### Technical Metrics
- **Analysis Time**: <5 seconds per feature (target)
- **Accuracy**: 70%+ vs manual/expert analysis
- **Coverage**: 100% of uploaded tracks analyzed

### User Metrics
- **Feature Usage**: >30% of tier users view feature
- **Engagement**: Average time on feature card >30 seconds
- **Actionability**: >20% of users take action after viewing

### Business Metrics
- **Conversion**: 10%+ increase in tier upgrades
- **Retention**: 5%+ increase in tier retention
- **NPS**: +5 point increase for tier users

---

## 🚀 Deployment Checklist

For each feature:

- [ ] Backend service implemented
- [ ] Unit tests written (>80% coverage)
- [ ] Database migration created
- [ ] API endpoint updated
- [ ] Frontend component created
- [ ] Integration tests written
- [ ] Documentation updated
- [ ] Staging deployment tested
- [ ] Production deployment
- [ ] Monitoring/logging configured
- [ ] User feedback collected

---

## 📚 References

- **Project Context**: `/home/dwood/tunescore/PROJECT_CONTEXT.md`
- **Audio Stack Audit**: `/home/dwood/tunescore/docs/AUDIO_ML_STACK_AUDIT.md`
- **Feature Prioritization**: `/home/dwood/tunescore/docs/FEATURE_PRIORITIZATION.md`
- **Existing Audio Services**: `/home/dwood/tunescore/backend/app/services/audio/`

---

**Next Steps**: Review briefs, approve implementation plan, begin Phase 1 development

