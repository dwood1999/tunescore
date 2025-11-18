# Feature Brief: TikTok Virality Predictor

**Priority**: 2.25  
**Phase**: 2 (Market Intelligence)  
**Effort**: 4/10 (3-4 days)  
**Impact**: 9/10

---

## 🎯 Overview

Predict TikTok virality potential by analyzing 15-30 second segments for repetition patterns, lyrical quotability, and hook placement. Train on viral TikTok audio features.

---

## 👥 User Stories

- Creator: "Will my track go viral on TikTok?"
- Developer: "Which demos have TikTok potential?"
- Monetizer: "Predict social media ROI"

---

## 🏗️ Architecture

```python
# backend/app/services/social/tiktok_predictor.py

class TikTokViralityPredictor:
    """Predict TikTok virality potential."""
    
    def predict(self, audio_path: str, lyrics: str, hook_data: dict) -> dict:
        """
        Predict TikTok virality.
        
        Returns:
            {
                "virality_score": 78,
                "optimal_clip_start": 45.2,
                "optimal_clip_duration": 15.0,
                "quotability_score": 82,
                "loop_potential": 85,
                "factors": {
                    "repetition": 90,
                    "hook_placement": 75,
                    "meme_potential": 70
                },
                "recommendations": [...]
            }
        """
        # 1. Analyze 15-30 second segments
        segments = self._analyze_segments(audio_path, hook_data)
        
        # 2. Lyrical quotability
        quotability = self._calculate_quotability(lyrics)
        
        # 3. Loop potential (repetition patterns)
        loop_potential = self._calculate_loop_potential(segments)
        
        # 4. Overall virality score
        virality_score = self._calculate_virality(
            segments, quotability, loop_potential
        )
        
        return {
            "virality_score": round(virality_score, 1),
            "optimal_clip_start": segments[0]["start_time"],
            "optimal_clip_duration": 15.0,
            "quotability_score": round(quotability, 1),
            "loop_potential": round(loop_potential, 1),
            "factors": {
                "repetition": round(loop_potential, 1),
                "hook_placement": round(segments[0]["hook_score"], 1),
                "meme_potential": round(quotability, 1)
            },
            "recommendations": self._generate_recommendations(virality_score)
        }
    
    def _analyze_segments(self, audio_path: str, hook_data: dict) -> list:
        """Analyze 15-30 second segments for virality."""
        import librosa
        import numpy as np
        
        y, sr = librosa.load(audio_path, sr=22050)
        duration = librosa.get_duration(y=y, sr=sr)
        
        segments = []
        for start in range(0, int(duration) - 15, 5):
            segment_y = y[start*sr:(start+15)*sr]
            
            # Energy + novelty (from hook detection)
            energy = np.mean(librosa.feature.rms(y=segment_y))
            
            # Repetition within segment
            repetition = self._measure_repetition(segment_y, sr)
            
            segments.append({
                "start_time": start,
                "energy": energy,
                "repetition": repetition,
                "hook_score": energy * repetition * 100
            })
        
        # Sort by hook score (best segment first)
        segments.sort(key=lambda x: x["hook_score"], reverse=True)
        return segments
    
    def _calculate_quotability(self, lyrics: str) -> float:
        """Calculate lyrical quotability (meme potential)."""
        if not lyrics:
            return 50.0
        
        lines = lyrics.split('\n')
        
        # Short, punchy lines are more quotable
        short_lines = sum(1 for line in lines if 3 <= len(line.split()) <= 8)
        quotability = (short_lines / len(lines)) * 100 if lines else 50
        
        # Bonus for repetition
        unique_lines = len(set(lines))
        repetition_bonus = (1 - unique_lines / len(lines)) * 20 if lines else 0
        
        return min(quotability + repetition_bonus, 100)
    
    def _calculate_loop_potential(self, segments: list) -> float:
        """Calculate how well segment loops (TikTok favors loops)."""
        # Best segment's repetition score
        return segments[0]["repetition"] * 100 if segments else 50
    
    def _measure_repetition(self, y: np.ndarray, sr: int) -> float:
        """Measure repetition within audio segment."""
        import librosa
        
        # Self-similarity matrix
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        similarity = np.dot(chroma.T, chroma) / (np.linalg.norm(chroma, axis=0) + 1e-8)
        
        # High off-diagonal values = repetition
        off_diagonal = similarity - np.eye(similarity.shape[0])
        repetition_score = np.mean(off_diagonal)
        
        return min(max(repetition_score, 0), 1)
    
    def _calculate_virality(
        self, segments: list, quotability: float, loop_potential: float
    ) -> float:
        """Calculate overall virality score."""
        hook_score = segments[0]["hook_score"] if segments else 50
        
        # Weighted average
        return (hook_score * 0.4) + (quotability * 0.3) + (loop_potential * 0.3)
```

---

## 🗄️ Database Schema

```python
class Analysis(Base):
    # ... existing fields ...
    tiktok_virality = Column(JSONB, nullable=True)  # NEW FIELD
```

---

## 🚀 Implementation Timeline

**Day 1-2**: Segment analysis, repetition detection  
**Day 3**: Quotability scoring, virality calculation  
**Day 4**: API integration, frontend component

---

## 📊 Success Metrics

- Accuracy: 70%+ correlation with actual TikTok performance (requires validation dataset)
- Usage: >40% of Developer tier users check virality score
- Engagement: Users spend >1 minute on virality insights

