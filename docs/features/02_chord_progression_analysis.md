# Feature Brief: Chord Progression Analysis

**Priority**: 3.0  
**Phase**: 1 (Quick Wins)  
**Effort**: 3/10 (2-3 days)  
**Impact**: 9/10

---

## 🎯 Overview

Extract chord progressions from audio tracks using Spotify's `basic-pitch` model (MIDI extraction). Analyze harmonic complexity, detect common progressions (I-V-vi-IV, etc.), identify key changes, and provide "familiar vs novel" scoring by comparing to hit song database.

---

## 👥 User Stories

### Creator Tier
- "What chords am I using in my song?" → Display chord progression
- "Is my progression too predictable?" → Familiarity score + suggestions
- "Where do I change keys?" → Modulation detection
- "How complex are my harmonies?" → Harmonic complexity score

### Developer Tier
- "Which artists use sophisticated chord progressions?" → Filter by complexity
- "Find tracks with similar harmonic structure" → Chord-based similarity search
- "Identify unique songwriting approaches" → Sort by novelty score

### Monetizer Tier
- "Analyze catalog harmonic diversity" → Portfolio analysis
- "Predict commercial appeal based on chord choices" → Familiarity vs novelty balance

---

## 🏗️ Architecture

### Data Flow
```
1. User uploads track → Audio file stored
2. Track analysis triggered → ChordAnalyzer.analyze()
3. MIDI extraction → basic-pitch model
   ├── Transcribe audio to MIDI
   ├── Extract note events
   └── Infer chord symbols
4. Chord analysis → ChordAnalyzer.analyze_progression()
   ├── Identify chord sequence
   ├── Detect key and mode
   ├── Calculate complexity metrics
   ├── Compare to hit database (familiarity)
   └── Detect modulations
5. Results stored → analyses.chord_analysis (JSONB)
6. Frontend displays → ChordProgressionCard.svelte
```

### Service Layer
```python
# backend/app/services/audio/chord_analyzer.py

import basic_pitch
from basic_pitch.inference import predict
import numpy as np
import librosa
from collections import Counter
import re

class ChordAnalyzer:
    """Analyze chord progressions using basic-pitch MIDI extraction."""
    
    # Common chord progressions in popular music
    COMMON_PROGRESSIONS = {
        "I-V-vi-IV": ["C", "G", "Am", "F"],  # "Don't Stop Believin'"
        "I-IV-V": ["C", "F", "G"],  # Classic rock
        "vi-IV-I-V": ["Am", "F", "C", "G"],  # "With or Without You"
        "I-vi-IV-V": ["C", "Am", "F", "G"],  # "50s progression"
        "I-V-vi-iii-IV-I-IV-V": ["C", "G", "Am", "Em", "F", "C", "F", "G"],  # "Canon"
        "ii-V-I": ["Dm", "G", "C"],  # Jazz turnaround
    }
    
    def __init__(self):
        self.model = None  # Lazy load
    
    def analyze(self, audio_path: str) -> dict:
        """
        Analyze chord progression from audio.
        
        Returns:
            {
                "chords": [
                    {"time": 0.0, "chord": "C", "duration": 2.0},
                    {"time": 2.0, "chord": "G", "duration": 2.0},
                    ...
                ],
                "key": "C major",
                "chord_sequence": ["C", "G", "Am", "F"],
                "unique_chords": 4,
                "progression_name": "I-V-vi-IV",
                "harmonic_complexity": 65,
                "familiarity_score": 85,
                "novelty_score": 15,
                "modulations": [
                    {"time": 45.2, "from_key": "C major", "to_key": "G major"}
                ],
                "recommendations": [...]
            }
        """
        # 1. Extract MIDI using basic-pitch
        midi_data = self._extract_midi(audio_path)
        
        # 2. Infer chords from MIDI notes
        chords = self._infer_chords(midi_data)
        
        # 3. Detect key and mode
        key, mode = self._detect_key(chords)
        
        # 4. Analyze progression
        chord_sequence = [c["chord"] for c in chords]
        unique_chords = len(set(chord_sequence))
        
        # 5. Identify progression pattern
        progression_name = self._identify_progression(chord_sequence, key)
        
        # 6. Calculate complexity
        harmonic_complexity = self._calculate_complexity(
            chord_sequence, unique_chords
        )
        
        # 7. Familiarity vs novelty
        familiarity_score = self._calculate_familiarity(progression_name, chord_sequence)
        novelty_score = 100 - familiarity_score
        
        # 8. Detect modulations (key changes)
        modulations = self._detect_modulations(chords)
        
        # 9. Generate recommendations
        recommendations = self._generate_recommendations(
            progression_name, harmonic_complexity, familiarity_score, modulations
        )
        
        return {
            "chords": chords,
            "key": f"{key} {mode}",
            "chord_sequence": chord_sequence,
            "unique_chords": unique_chords,
            "progression_name": progression_name,
            "harmonic_complexity": round(harmonic_complexity, 1),
            "familiarity_score": round(familiarity_score, 1),
            "novelty_score": round(novelty_score, 1),
            "modulations": modulations,
            "recommendations": recommendations,
        }
    
    def _extract_midi(self, audio_path: str) -> dict:
        """Extract MIDI data using basic-pitch."""
        # basic-pitch returns (model_output, midi_data, note_events)
        model_output, midi_data, note_events = predict(audio_path)
        
        return {
            "note_events": note_events,
            "midi_data": midi_data,
        }
    
    def _infer_chords(self, midi_data: dict) -> list[dict]:
        """
        Infer chord symbols from MIDI note events.
        
        Groups notes by time windows and identifies chord types.
        """
        note_events = midi_data["note_events"]
        
        # Group notes into time windows (500ms)
        window_size = 0.5  # seconds
        chords = []
        
        # Sort notes by start time
        sorted_notes = sorted(note_events, key=lambda x: x["start_time"])
        
        current_time = 0
        current_notes = []
        
        for note in sorted_notes:
            if note["start_time"] - current_time > window_size:
                # Process accumulated notes as a chord
                if current_notes:
                    chord_symbol = self._notes_to_chord(current_notes)
                    chords.append({
                        "time": current_time,
                        "chord": chord_symbol,
                        "duration": note["start_time"] - current_time,
                    })
                
                current_time = note["start_time"]
                current_notes = [note]
            else:
                current_notes.append(note)
        
        # Process final chord
        if current_notes:
            chord_symbol = self._notes_to_chord(current_notes)
            chords.append({
                "time": current_time,
                "chord": chord_symbol,
                "duration": 2.0,  # Default duration
            })
        
        return chords
    
    def _notes_to_chord(self, notes: list[dict]) -> str:
        """
        Convert MIDI notes to chord symbol.
        
        Simplified chord detection (major, minor, diminished, augmented).
        """
        if not notes:
            return "N"  # No chord
        
        # Extract pitch classes (0-11)
        pitch_classes = [note["pitch"] % 12 for note in notes]
        pitch_classes = sorted(set(pitch_classes))
        
        if len(pitch_classes) < 2:
            return self._pitch_to_note_name(pitch_classes[0])
        
        # Detect chord type by intervals
        root = pitch_classes[0]
        intervals = [(pc - root) % 12 for pc in pitch_classes]
        
        # Major triad: 0, 4, 7
        if set([0, 4, 7]).issubset(set(intervals)):
            return self._pitch_to_note_name(root)
        
        # Minor triad: 0, 3, 7
        if set([0, 3, 7]).issubset(set(intervals)):
            return self._pitch_to_note_name(root) + "m"
        
        # Diminished: 0, 3, 6
        if set([0, 3, 6]).issubset(set(intervals)):
            return self._pitch_to_note_name(root) + "dim"
        
        # Augmented: 0, 4, 8
        if set([0, 4, 8]).issubset(set(intervals)):
            return self._pitch_to_note_name(root) + "aug"
        
        # Dominant 7th: 0, 4, 7, 10
        if set([0, 4, 7, 10]).issubset(set(intervals)):
            return self._pitch_to_note_name(root) + "7"
        
        # Major 7th: 0, 4, 7, 11
        if set([0, 4, 7, 11]).issubset(set(intervals)):
            return self._pitch_to_note_name(root) + "maj7"
        
        # Minor 7th: 0, 3, 7, 10
        if set([0, 3, 7, 10]).issubset(set(intervals)):
            return self._pitch_to_note_name(root) + "m7"
        
        # Default: just return root note
        return self._pitch_to_note_name(root)
    
    def _pitch_to_note_name(self, pitch: int) -> str:
        """Convert MIDI pitch to note name."""
        notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        return notes[pitch % 12]
    
    def _detect_key(self, chords: list[dict]) -> tuple[str, str]:
        """Detect key and mode from chord progression."""
        # Count chord occurrences
        chord_counts = Counter([c["chord"] for c in chords])
        
        # Most common chord is likely the tonic
        if not chord_counts:
            return "C", "major"
        
        tonic = chord_counts.most_common(1)[0][0]
        
        # Detect mode (major vs minor) from chord quality
        if "m" in tonic:
            mode = "minor"
            tonic = tonic.replace("m", "")
        else:
            mode = "major"
        
        return tonic, mode
    
    def _identify_progression(self, chord_sequence: list[str], key: str) -> str:
        """Identify common chord progression patterns."""
        # Normalize chord sequence (remove duplicates, limit to 8 chords)
        unique_sequence = []
        for chord in chord_sequence:
            if not unique_sequence or chord != unique_sequence[-1]:
                unique_sequence.append(chord)
        
        # Limit to first 8 chords
        unique_sequence = unique_sequence[:8]
        
        # Check against common progressions
        for name, pattern in self.COMMON_PROGRESSIONS.items():
            if unique_sequence == pattern:
                return name
        
        # Check for partial matches
        for name, pattern in self.COMMON_PROGRESSIONS.items():
            if len(unique_sequence) >= 4 and unique_sequence[:4] == pattern[:4]:
                return f"{name} (variant)"
        
        return "Custom progression"
    
    def _calculate_complexity(
        self, chord_sequence: list[str], unique_chords: int
    ) -> float:
        """
        Calculate harmonic complexity score (0-100).
        
        Factors:
        - Number of unique chords (more = higher complexity)
        - Chord types (7ths, extensions = higher complexity)
        - Chord changes per minute
        """
        # 1. Unique chord score (0-40 points)
        if unique_chords <= 3:
            unique_score = 10
        elif unique_chords <= 5:
            unique_score = 20
        elif unique_chords <= 8:
            unique_score = 30
        else:
            unique_score = 40
        
        # 2. Chord type complexity (0-40 points)
        complex_chords = sum(
            1 for chord in chord_sequence
            if any(ext in chord for ext in ["7", "9", "11", "13", "dim", "aug", "sus"])
        )
        type_score = min(complex_chords * 5, 40)
        
        # 3. Progression novelty (0-20 points)
        # Non-standard progressions get higher scores
        progression_name = self._identify_progression(chord_sequence, "")
        if progression_name == "Custom progression":
            novelty_score = 20
        elif "variant" in progression_name:
            novelty_score = 10
        else:
            novelty_score = 5
        
        return unique_score + type_score + novelty_score
    
    def _calculate_familiarity(
        self, progression_name: str, chord_sequence: list[str]
    ) -> float:
        """
        Calculate familiarity score (0-100).
        
        Higher = more familiar (common progressions)
        Lower = more novel (unique progressions)
        """
        # Common progressions are highly familiar
        if progression_name in self.COMMON_PROGRESSIONS:
            return 90.0
        elif "variant" in progression_name:
            return 70.0
        else:
            # Calculate based on chord commonality
            common_chords = ["C", "G", "Am", "F", "D", "Em", "A", "E", "Dm", "Bm"]
            common_count = sum(1 for chord in chord_sequence if chord in common_chords)
            
            if not chord_sequence:
                return 50.0
            
            return (common_count / len(chord_sequence)) * 100
    
    def _detect_modulations(self, chords: list[dict]) -> list[dict]:
        """Detect key changes (modulations) in the progression."""
        # Simplified: detect when chord patterns shift significantly
        # In production, use more sophisticated key detection
        
        modulations = []
        window_size = 8  # Analyze 8-chord windows
        
        for i in range(0, len(chords) - window_size, window_size):
            window = chords[i:i+window_size]
            key, mode = self._detect_key(window)
            
            if i > 0:
                prev_window = chords[i-window_size:i]
                prev_key, prev_mode = self._detect_key(prev_window)
                
                if key != prev_key or mode != prev_mode:
                    modulations.append({
                        "time": window[0]["time"],
                        "from_key": f"{prev_key} {prev_mode}",
                        "to_key": f"{key} {mode}",
                    })
        
        return modulations
    
    def _generate_recommendations(
        self, progression_name: str, complexity: float, familiarity: float, modulations: list
    ) -> list[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Complexity recommendations
        if complexity < 30:
            recommendations.append(
                "Try adding 7th chords or extensions to increase harmonic interest."
            )
        elif complexity > 70:
            recommendations.append(
                "Your progression is complex. Ensure it serves the song's emotional arc."
            )
        
        # Familiarity recommendations
        if familiarity > 80:
            recommendations.append(
                f"You're using a very common progression ({progression_name}). "
                "Consider adding a unique twist or bridge section."
            )
        elif familiarity < 30:
            recommendations.append(
                "Your progression is highly unique. Ensure it's memorable and singable."
            )
        
        # Modulation recommendations
        if len(modulations) == 0:
            recommendations.append(
                "No key changes detected. Consider a modulation for the bridge or final chorus."
            )
        elif len(modulations) > 3:
            recommendations.append(
                "Multiple key changes detected. Ensure transitions feel natural."
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
    chord_analysis = Column(JSONB, nullable=True)  # NEW FIELD
```

---

## 📦 Dependencies

### New Dependencies
```toml
# backend/pyproject.toml
basic-pitch = "^0.2.5"  # Spotify's MIDI extraction model
```

### Installation
```bash
cd /home/dwood/tunescore/backend
source venv/bin/activate
poetry add basic-pitch
```

---

## 🎨 Frontend Components

### ChordProgressionCard.svelte
```svelte
<script lang="ts">
  import { Card, Badge, ProgressBar } from '$lib/components/ui';
  
  export let chordAnalysis: {
    chords: Array<{time: number; chord: string; duration: number}>;
    key: string;
    chord_sequence: string[];
    unique_chords: number;
    progression_name: string;
    harmonic_complexity: number;
    familiarity_score: number;
    novelty_score: number;
    modulations: Array<any>;
    recommendations: string[];
  };
  
  function formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }
</script>

<Card title="Chord Progression">
  <div class="space-y-4">
    <!-- Key & Progression -->
    <div class="flex justify-between items-center">
      <div>
        <span class="text-sm text-gray-600">Key</span>
        <p class="text-lg font-semibold">{chordAnalysis.key}</p>
      </div>
      <div class="text-right">
        <span class="text-sm text-gray-600">Progression</span>
        <p class="text-sm font-mono">{chordAnalysis.progression_name}</p>
      </div>
    </div>
    
    <!-- Chord Sequence -->
    <div>
      <h4 class="font-semibold mb-2">Chord Sequence</h4>
      <div class="flex flex-wrap gap-2">
        {#each chordAnalysis.chord_sequence.slice(0, 12) as chord}
          <Badge color="blue">{chord}</Badge>
        {/each}
        {#if chordAnalysis.chord_sequence.length > 12}
          <Badge color="gray">+{chordAnalysis.chord_sequence.length - 12} more</Badge>
        {/if}
      </div>
    </div>
    
    <!-- Complexity & Familiarity -->
    <div class="grid grid-cols-2 gap-4">
      <div>
        <span class="text-sm text-gray-600">Harmonic Complexity</span>
        <ProgressBar value={chordAnalysis.harmonic_complexity} max={100} />
        <span class="text-xs">{chordAnalysis.harmonic_complexity}/100</span>
      </div>
      <div>
        <span class="text-sm text-gray-600">Familiarity</span>
        <ProgressBar value={chordAnalysis.familiarity_score} max={100} color="purple" />
        <span class="text-xs">{chordAnalysis.familiarity_score}/100</span>
      </div>
    </div>
    
    <!-- Modulations -->
    {#if chordAnalysis.modulations.length > 0}
      <div>
        <h4 class="font-semibold mb-2">Key Changes</h4>
        {#each chordAnalysis.modulations as mod}
          <div class="text-sm p-2 bg-purple-50 rounded mb-2">
            <span class="font-mono">{formatTime(mod.time)}</span>:
            {mod.from_key} → {mod.to_key}
          </div>
        {/each}
      </div>
    {/if}
    
    <!-- Recommendations -->
    {#if chordAnalysis.recommendations.length > 0}
      <div>
        <h4 class="font-semibold mb-2">Recommendations</h4>
        <ul class="list-disc list-inside space-y-1 text-sm">
          {#each chordAnalysis.recommendations as rec}
            <li>{rec}</li>
          {/each}
        </ul>
      </div>
    {/if}
  </div>
</Card>
```

---

## ✅ Testing Strategy

### Unit Tests
```python
# backend/app/tests/test_chord_analyzer.py

import pytest
from app.services.audio.chord_analyzer import ChordAnalyzer

def test_detect_common_progression():
    analyzer = ChordAnalyzer()
    result = analyzer.analyze("test_files/i_v_vi_iv_progression.wav")
    
    assert result["progression_name"] == "I-V-vi-IV"
    assert result["familiarity_score"] > 80

def test_detect_key():
    analyzer = ChordAnalyzer()
    result = analyzer.analyze("test_files/c_major_track.wav")
    
    assert "C" in result["key"]
    assert "major" in result["key"]
```

---

## 📊 Success Metrics

### Technical Metrics
- Analysis time: <5 seconds per track
- Accuracy: 70%+ chord detection accuracy (vs manual transcription)
- Coverage: 100% of uploaded tracks analyzed

### User Metrics
- Feature usage: >40% of Creator tier users view chord analysis
- Engagement: Average time on chord card >45 seconds
- Actionability: >25% of users modify chord progressions after viewing analysis

---

## 🚀 Implementation Timeline

### Day 1: MIDI Extraction
- [ ] Integrate basic-pitch model
- [ ] Extract MIDI from audio
- [ ] Infer chord symbols from MIDI

### Day 2: Chord Analysis
- [ ] Detect key and mode
- [ ] Identify progression patterns
- [ ] Calculate complexity and familiarity
- [ ] Detect modulations

### Day 3: Integration & Frontend
- [ ] Add chord analysis to track flow
- [ ] Create database migration
- [ ] Update API endpoints
- [ ] Create `ChordProgressionCard.svelte`
- [ ] Deploy to staging

---

## 📚 References

- **basic-pitch**: https://github.com/spotify/basic-pitch
- **Chord Detection Paper**: https://arxiv.org/abs/2010.11930
- **Common Progressions**: https://www.hooktheory.com/theorytab/common-chord-progressions

