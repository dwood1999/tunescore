# TuneScore: Feature Prioritization Matrix

**Date**: November 2, 2025  
**Purpose**: Impact/effort scoring to select initial feature bundle for implementation

---

## 🎯 Scoring Methodology

### Impact Score (1-10)
- **Market Differentiation** (0-3): How unique is this feature?
- **User Value** (0-3): How much does it help users achieve their goals?
- **Revenue Potential** (0-2): Does it drive conversions/upgrades?
- **Technical Leverage** (0-2): Does it enable other features?

### Effort Score (1-10)
- **Development Time** (0-3): How long to implement?
- **Complexity** (0-3): How difficult is the code?
- **Dependencies** (0-2): New libraries/infrastructure needed?
- **Risk** (0-2): How likely to encounter blockers?

### Priority Score = Impact / Effort
- **High Priority**: >1.5 (do first)
- **Medium Priority**: 0.8-1.5 (do second)
- **Low Priority**: <0.8 (defer or skip)

---

## 📊 Feature Scoring Matrix

| # | Feature | Impact | Effort | Priority | Tier | Phase |
|---|---------|--------|--------|----------|------|-------|
| 1 | **Mastering Quality Detection** | 8 | 2 | **4.0** | All | 1 |
| 2 | **Chord Progression Analysis** | 9 | 3 | **3.0** | Creator/Developer | 1 |
| 3 | **AI Lyric Critic & Rewrite** | 8 | 3 | **2.7** | Creator | 1 |
| 4 | **Mastering Reference Comparison** | 7 | 3 | **2.3** | Creator | 1 |
| 5 | **Vocal Isolation (Spleeter)** | 9 | 4 | **2.25** | All | 2 |
| 6 | **TikTok Virality Predictor** | 9 | 4 | **2.25** | Developer | 2 |
| 7 | **Sync Licensing Matcher** | 8 | 4 | **2.0** | Monetizer | 2 |
| 8 | **Vocal Performance Analysis** | 7 | 4 | **1.75** | Creator | 2 |
| 9 | **Beat & Flow Analysis (Hip-Hop)** | 6 | 4 | **1.5** | Creator | 3 |
| 10 | **Stem-Level Mixing Analysis** | 7 | 5 | **1.4** | Creator | 3 |
| 11 | **Career Trajectory Modeling** | 8 | 6 | **1.33** | Developer | 3 |
| 12 | **Global Market Resonance (Expanded)** | 7 | 5 | **1.4** | Monetizer | 3 |
| 13 | **Playlist Ecosystem Mapper** | 6 | 5 | **1.2** | Developer | 3 |
| 14 | **Reference Track Matching** | 5 | 3 | **1.67** | Creator | 2 |
| 15 | **Lyrical Mood Board Generator** | 6 | 3 | **2.0** | Creator | 2 |
| 16 | **A&R Pitch Deck Builder** | 7 | 4 | **1.75** | Developer | 2 |
| 17 | **Press Release Generator** | 5 | 2 | **2.5** | Creator | 1 |
| 18 | **Vocal Isolation (Demucs - SOTA)** | 9 | 7 | **1.29** | All | 4 |
| 19 | **AI Cover Detection** | 7 | 7 | **1.0** | All | 4 |
| 20 | **Copyright Risk Detector** | 6 | 6 | **1.0** | Monetizer | 4 |

---

## 🏆 Top 10 Features (Priority Score >2.0)

### 1. Mastering Quality Detection (Priority: 4.0)
**Impact: 8/10** | **Effort: 2/10**

**Why High Impact:**
- Market Differentiation (3/3): No competitors offer LUFS/DR analysis
- User Value (3/3): Instant feedback on mix quality
- Revenue Potential (1/2): Drives Creator tier upgrades
- Technical Leverage (1/2): Enables mastering reference comparison

**Why Low Effort:**
- Development Time (1/3): 1-2 days
- Complexity (0/3): Simple LUFS measurement
- Dependencies (1/2): `pyloudnorm` (pip install)
- Risk (0/2): Well-documented library

**User Stories:**
- Creator: "Is my track loud enough for Spotify?"
- Creator: "Am I over-compressing (loudness war)?"
- Developer: "Which demos have pro-level mastering?"

**Technical Notes:**
- Use `pyloudnorm` for LUFS measurement
- Compare to platform targets (Spotify: -14 LUFS, Apple: -16 LUFS)
- Calculate DR (Dynamic Range) score
- Flag over-compression (DR < 6)

---

### 2. Chord Progression Analysis (Priority: 3.0)
**Impact: 9/10** | **Effort: 3/10**

**Why High Impact:**
- Market Differentiation (3/3): Unique songwriting insights
- User Value (3/3): Helps creators understand their harmonic choices
- Revenue Potential (1/2): Drives Creator tier upgrades
- Technical Leverage (2/2): Enables "familiar vs novel" scoring, key change detection

**Why Low Effort:**
- Development Time (1/3): 2-3 days
- Complexity (1/3): Use pre-trained model
- Dependencies (1/2): `basic-pitch` (Spotify's model)
- Risk (0/2): Well-tested open-source model

**User Stories:**
- Creator: "What chords am I using?"
- Creator: "Is my progression too predictable?"
- Developer: "Which artists use complex harmonies?"

**Technical Notes:**
- Use Spotify's `basic-pitch` model (MIDI extraction)
- Extract chord progressions from MIDI
- Analyze: common progressions (I-V-vi-IV), harmonic complexity, key changes
- Compare to hit database for "familiar vs novel" scoring

---

### 3. AI Lyric Critic & Rewrite (Priority: 2.7)
**Impact: 8/10** | **Effort: 3/10**

**Why High Impact:**
- Market Differentiation (2/3): Few competitors offer AI feedback
- User Value (3/3): Actionable songwriting improvements
- Revenue Potential (2/2): Premium feature for Creator tier
- Technical Leverage (1/2): Uses existing lyrical genome

**Why Low Effort:**
- Development Time (1/3): 1-2 days
- Complexity (1/3): Prompt engineering (Claude/GPT-4)
- Dependencies (0/2): Already installed (anthropic, openai)
- Risk (1/2): API costs (need cost governor)

**User Stories:**
- Creator: "How can I improve my lyrics?"
- Creator: "Suggest alternative rhymes for this line"
- Creator: "Is my verse too repetitive?"

**Technical Notes:**
- Use Claude 3.5 Sonnet or GPT-4
- Input: lyrics + songwriting quality breakdown
- Output: critique + rewrite suggestions + rhyme scheme improvements
- Implement cost governor (max $0.10 per analysis)

---

### 4. Mastering Reference Comparison (Priority: 2.3)
**Impact: 7/10** | **Effort: 3/10**

**Why High Impact:**
- Market Differentiation (2/3): Unique visual tool
- User Value (3/3): Actionable EQ suggestions
- Revenue Potential (1/2): Drives Creator tier upgrades
- Technical Leverage (1/2): Uses existing sonic genome

**Why Low Effort:**
- Development Time (1/3): 1 day
- Complexity (1/3): Spectral subtraction
- Dependencies (0/2): None (use librosa)
- Risk (1/2): Visualization complexity

**User Stories:**
- Creator: "How does my mix compare to this reference track?"
- Creator: "What EQ adjustments should I make?"
- Creator: "Where is my mix too muddy/bright?"

**Technical Notes:**
- Let users upload a "reference track"
- Extract spectral features (STFT) from both tracks
- Generate spectral diff heatmap (frequency vs time)
- Suggest EQ adjustments: "Add +2dB at 5kHz for more air"

---

### 5. Vocal Isolation (Spleeter) (Priority: 2.25)
**Impact: 9/10** | **Effort: 4/10**

**Why High Impact:**
- Market Differentiation (3/3): Enables 10+ downstream features
- User Value (2/3): Useful on its own, more valuable with analysis
- Revenue Potential (2/2): Premium feature for all tiers
- Technical Leverage (2/2): Unlocks vocal analysis, mixing analysis, etc.

**Why Medium Effort:**
- Development Time (2/3): 3-5 days
- Complexity (1/3): Pre-trained model
- Dependencies (1/2): `spleeter` (TensorFlow, CPU-friendly)
- Risk (0/2): Well-documented library

**User Stories:**
- Creator: "Isolate vocals for remix/sampling"
- Creator: "Analyze my vocal performance separately"
- Developer: "Compare vocal production quality"

**Technical Notes:**
- Use Spleeter 2-stem model (vocals + accompaniment)
- CPU-friendly (no GPU required)
- Store stems in JSONB or separate files
- Enable downstream features: vocal analysis, mixing analysis

---

### 6. TikTok Virality Predictor (Priority: 2.25)
**Impact: 9/10** | **Effort: 4/10**

**Why High Impact:**
- Market Differentiation (3/3): Highly unique feature
- User Value (3/3): Actionable social media strategy
- Revenue Potential (2/2): Drives Developer tier upgrades
- Technical Leverage (1/2): Uses existing hook detection

**Why Medium Effort:**
- Development Time (2/3): 3-4 days
- Complexity (1/3): Extend existing hook detection
- Dependencies (0/2): None (use existing features)
- Risk (1/2): Need TikTok training data

**User Stories:**
- Creator: "Will my track go viral on TikTok?"
- Developer: "Which demos have TikTok potential?"
- Monetizer: "Predict social media ROI"

**Technical Notes:**
- Analyze 15-30 second segments for:
  - Repetition patterns (TikTok favors loops)
  - Lyrical "quotability" (meme potential)
  - Hook placement timing
- Train on viral TikTok audio features (scrape TikTok trending sounds)
- Output: virality score (0-100) + optimal clip timing

---

### 7. Sync Licensing Matcher (Priority: 2.0)
**Impact: 8/10** | **Effort: 4/10**

**Why High Impact:**
- Market Differentiation (2/3): Few competitors offer this
- User Value (3/3): Revenue-generating feature
- Revenue Potential (2/2): Drives Monetizer tier upgrades
- Technical Leverage (1/2): Uses existing genre/theme detection

**Why Medium Effort:**
- Development Time (2/3): 4-5 days
- Complexity (1/3): Use pre-trained AST model
- Dependencies (1/2): `ast-finetuned-audioset` (already using similar)
- Risk (0/2): Well-tested approach

**User Stories:**
- Monetizer: "Which tracks fit car commercials?"
- Monetizer: "Find sync opportunities for my catalog"
- Developer: "Pitch tracks for TV/film placements"

**Technical Notes:**
- Mood tagging: epic, melancholic, energetic, corporate, cinematic
- Use Audio Spectrogram Transformer (AST) for mood classification
- Match to: TV genres, commercial styles, game soundtracks
- Output: "This track fits: car commercials, sports highlights, indie film credits"

---

### 8. Lyrical Mood Board Generator (Priority: 2.0)
**Impact: 6/10** | **Effort: 3/10**

**Why Medium Impact:**
- Market Differentiation (2/3): Creative tool, not analytical
- User Value (2/3): Nice-to-have, not essential
- Revenue Potential (1/2): Drives Creator tier upgrades
- Technical Leverage (1/2): Uses existing lyrical genome

**Why Low Effort:**
- Development Time (1/3): 1-2 days
- Complexity (1/3): API integration
- Dependencies (1/2): DALL-E 3 or Stable Diffusion API
- Risk (0/2): Well-documented APIs

**User Stories:**
- Creator: "Generate album art concepts from my lyrics"
- Creator: "Visualize the mood of my song"
- Developer: "Create pitch deck visuals"

**Technical Notes:**
- Use DALL-E 3 or Stable Diffusion API
- Input: lyrical themes + emotional arc + genre
- Output: 3-5 album art concepts
- Store variations for A&R pitch decks

---

### 9. Press Release Generator (Priority: 2.5)
**Impact: 5/10** | **Effort: 2/10**

**Why Medium Impact:**
- Market Differentiation (1/3): Common feature
- User Value (2/3): Saves time, not game-changing
- Revenue Potential (1/2): Drives Creator tier upgrades
- Technical Leverage (1/2): Uses existing analysis data

**Why Low Effort:**
- Development Time (1/3): 1 day
- Complexity (0/3): Simple prompt engineering
- Dependencies (0/2): Already installed (Claude/GPT-4)
- Risk (1/2): API costs

**User Stories:**
- Creator: "Generate EPK copy for my track"
- Creator: "Write a press release for my album"
- Developer: "Create one-pagers for label pitches"

**Technical Notes:**
- Auto-generate EPK (Electronic Press Kit) copy
- Input: sonic genome, RIYL data, lyrical themes
- Output: "Artist X blends [genre] with [genre], evoking [reference artists]"
- Template-based with AI enhancement

---

### 10. Reference Track Matching (Priority: 1.67)
**Impact: 5/10** | **Effort: 3/10**

**Why Medium Impact:**
- Market Differentiation (1/3): Similar to existing RIYL
- User Value (2/3): Useful for DJs/producers
- Revenue Potential (1/2): Drives Creator tier upgrades
- Technical Leverage (1/2): Extends existing embeddings

**Why Low Effort:**
- Development Time (1/3): 1-2 days
- Complexity (1/3): Extend existing RIYL
- Dependencies (0/2): None (use existing embeddings)
- Risk (1/2): Need BPM/key compatibility logic

**User Stories:**
- Creator: "Find tracks that mix well with mine"
- Creator: "Which Spotify playlists should I target?"
- Developer: "Predict playlist placement"

**Technical Notes:**
- Expand RIYL to include:
  - "This track sounds like [Artist] meets [Artist]"
  - BPM + key compatibility for DJ sets
  - "Playlist placement prediction" (which Spotify editorial playlists fit?)

---

## 📋 Recommended Feature Bundles

### Bundle A: "Quick Wins" (Phase 1 - 1-2 weeks)
**Goal**: Immediate value, minimal dependencies

1. **Mastering Quality Detection** (Priority: 4.0)
2. **Chord Progression Analysis** (Priority: 3.0)
3. **AI Lyric Critic** (Priority: 2.7)
4. **Press Release Generator** (Priority: 2.5)

**Total Effort**: 8/10 (1-2 weeks)  
**Total Impact**: 26/40 (65% average impact)  
**Rationale**: All CPU-friendly, no new infrastructure, builds on existing features

---

### Bundle B: "Vocal Intelligence" (Phase 2 - 2-3 weeks)
**Goal**: Unlock vocal analysis capabilities

5. **Vocal Isolation (Spleeter)** (Priority: 2.25)
6. **Vocal Performance Analysis** (Priority: 1.75)
7. **Mastering Reference Comparison** (Priority: 2.3)

**Total Effort**: 11/10 (2-3 weeks)  
**Total Impact**: 23/30 (77% average impact)  
**Rationale**: Spleeter unlocks downstream vocal features, high user value

---

### Bundle C: "Market Intelligence" (Phase 3 - 3-4 weeks)
**Goal**: Revenue-generating features for Developer/Monetizer tiers

8. **TikTok Virality Predictor** (Priority: 2.25)
9. **Sync Licensing Matcher** (Priority: 2.0)
10. **A&R Pitch Deck Builder** (Priority: 1.75)

**Total Effort**: 12/10 (3-4 weeks)  
**Total Impact**: 24/30 (80% average impact)  
**Rationale**: Aligns with "Monetizer" tier, drives revenue

---

### Bundle D: "Advanced ML" (Phase 4 - 4-6 weeks)
**Goal**: Cutting-edge features requiring GPU infrastructure

11. **Vocal Isolation (Demucs - SOTA)** (Priority: 1.29)
12. **AI Cover Detection** (Priority: 1.0)
13. **Career Trajectory Modeling** (Priority: 1.33)

**Total Effort**: 20/10 (4-6 weeks)  
**Total Impact**: 24/30 (80% average impact)  
**Rationale**: Requires GPU investment, high differentiation

---

## 🎯 Final Recommendation: Bundle A + Bundle B

### Phase 1: Quick Wins (Weeks 1-2)
1. Mastering Quality Detection
2. Chord Progression Analysis
3. AI Lyric Critic
4. Press Release Generator

### Phase 2: Vocal Intelligence (Weeks 3-5)
5. Vocal Isolation (Spleeter)
6. Mastering Reference Comparison
7. Vocal Performance Analysis

**Total Timeline**: 5 weeks  
**Total Features**: 7  
**Average Priority Score**: 2.5 (High Priority)

**Why This Bundle:**
- ✅ No GPU required (CPU-friendly)
- ✅ Minimal new dependencies
- ✅ Builds on existing infrastructure
- ✅ High user value across all tiers
- ✅ Enables future features (vocal isolation → mixing analysis)
- ✅ Market differentiation (chord progressions, mastering quality)

---

## 📊 Feature Details (Full Scoring)

### 1. Mastering Quality Detection
**Impact Breakdown:**
- Market Differentiation: 3/3 (no competitors offer this)
- User Value: 3/3 (instant feedback on mix quality)
- Revenue Potential: 1/2 (drives Creator upgrades)
- Technical Leverage: 1/2 (enables reference comparison)

**Effort Breakdown:**
- Development Time: 1/3 (1-2 days)
- Complexity: 0/3 (simple LUFS measurement)
- Dependencies: 1/2 (pyloudnorm)
- Risk: 0/2 (well-documented)

---

### 2. Chord Progression Analysis
**Impact Breakdown:**
- Market Differentiation: 3/3 (unique songwriting insights)
- User Value: 3/3 (helps creators understand harmonies)
- Revenue Potential: 1/2 (drives Creator upgrades)
- Technical Leverage: 2/2 (enables "familiar vs novel" scoring)

**Effort Breakdown:**
- Development Time: 1/3 (2-3 days)
- Complexity: 1/3 (use pre-trained model)
- Dependencies: 1/2 (basic-pitch)
- Risk: 0/2 (well-tested)

---

### 3. AI Lyric Critic & Rewrite
**Impact Breakdown:**
- Market Differentiation: 2/3 (few competitors offer this)
- User Value: 3/3 (actionable improvements)
- Revenue Potential: 2/2 (premium Creator feature)
- Technical Leverage: 1/2 (uses existing lyrical genome)

**Effort Breakdown:**
- Development Time: 1/3 (1-2 days)
- Complexity: 1/3 (prompt engineering)
- Dependencies: 0/2 (already installed)
- Risk: 1/2 (API costs)

---

### 4. Mastering Reference Comparison
**Impact Breakdown:**
- Market Differentiation: 2/3 (unique visual tool)
- User Value: 3/3 (actionable EQ suggestions)
- Revenue Potential: 1/2 (drives Creator upgrades)
- Technical Leverage: 1/2 (uses existing sonic genome)

**Effort Breakdown:**
- Development Time: 1/3 (1 day)
- Complexity: 1/3 (spectral subtraction)
- Dependencies: 0/2 (use librosa)
- Risk: 1/2 (visualization complexity)

---

### 5. Vocal Isolation (Spleeter)
**Impact Breakdown:**
- Market Differentiation: 3/3 (enables 10+ features)
- User Value: 2/3 (useful on its own)
- Revenue Potential: 2/2 (premium feature)
- Technical Leverage: 2/2 (unlocks vocal/mixing analysis)

**Effort Breakdown:**
- Development Time: 2/3 (3-5 days)
- Complexity: 1/3 (pre-trained model)
- Dependencies: 1/2 (spleeter)
- Risk: 0/2 (well-documented)

---

### 6. TikTok Virality Predictor
**Impact Breakdown:**
- Market Differentiation: 3/3 (highly unique)
- User Value: 3/3 (actionable social strategy)
- Revenue Potential: 2/2 (drives Developer upgrades)
- Technical Leverage: 1/2 (uses existing hook detection)

**Effort Breakdown:**
- Development Time: 2/3 (3-4 days)
- Complexity: 1/3 (extend hook detection)
- Dependencies: 0/2 (none)
- Risk: 1/2 (need TikTok data)

---

### 7. Sync Licensing Matcher
**Impact Breakdown:**
- Market Differentiation: 2/3 (few competitors)
- User Value: 3/3 (revenue-generating)
- Revenue Potential: 2/2 (drives Monetizer upgrades)
- Technical Leverage: 1/2 (uses existing genre/theme)

**Effort Breakdown:**
- Development Time: 2/3 (4-5 days)
- Complexity: 1/3 (use AST model)
- Dependencies: 1/2 (ast-finetuned-audioset)
- Risk: 0/2 (well-tested)

---

## 🚀 Next Steps

1. **Review & Approve**: Stakeholder sign-off on Bundle A + Bundle B
2. **Draft Technical Briefs**: Architecture/data flow for each feature
3. **Define Success Metrics**: KPIs for each feature
4. **Prototype Phase 1**: Start with Mastering Quality Detection

---

**Decision Required**: Approve Bundle A + Bundle B for implementation?

