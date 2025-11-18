# API Model Optimization Guide

## Best Models for Each Task

Based on 2024/2025 API documentation and pricing, here are the recommended models for each TuneScore feature:

### 1. **Pitch Copy Generation** (Marketing Copy)
**Task**: Generate elevator pitches, EPK descriptions, sync licensing pitches

**Recommended Models** (in priority order):
1. **Claude 3.5 Sonnet** (`claude-3-5-sonnet-20241022`)
   - Best quality for creative writing
   - Excellent at professional tone
   - ~$3/1M input, ~$15/1M output tokens
   - **Use for**: High-quality pitches when cost allows

2. **GPT-4o Mini** (`gpt-4o-mini`)
   - Excellent quality/cost ratio
   - Very good at marketing copy
   - ~$0.15/1M input, ~$0.60/1M output tokens
   - **Use for**: Production (best value)

3. **DeepSeek Chat** (`deepseek-chat`)
   - Very cheap (~$0.28/1M input, $0.42/1M output)
   - Good quality for simpler prompts
   - **Use for**: Fallback when cost is critical

**Current Implementation**: Uses Claude Haiku → GPT-4o Mini → DeepSeek fallback
**Recommendation**: Switch priority to GPT-4o Mini first (best value), then Claude 3.5 Sonnet for premium

---

### 2. **Lyric Critique** (Detailed Analysis)
**Task**: Analyze lyrics, provide feedback, suggest improvements

**Recommended Models**:
1. **Claude 3.5 Sonnet** (`claude-3-5-sonnet-20241022`)
   - Best for nuanced critique and creativity
   - Excellent at understanding context and emotion
   - **Use for**: High-quality critiques

2. **GPT-4o** (`gpt-4o`)
   - Very good at analysis and structured feedback
   - Better at following instructions
   - ~$2.50/1M input, ~$10/1M output
   - **Use for**: Alternative if Claude unavailable

3. **Gemini 2.0 Flash** (`gemini-2.0-flash-exp`)
   - Good for analysis tasks
   - Very fast and cheap
   - **Use for**: Cost-sensitive scenarios

**Current Implementation**: Uses Claude 3.5 Sonnet with fallback
**Recommendation**: Keep Claude 3.5 Sonnet as primary (best quality), add GPT-4o as fallback

---

### 3. **Tag Classification** (Mood/Commercial Tags)
**Task**: Classify tracks by mood, commercial viability, use cases

**Current Implementation**: Rule-based (no API cost) ✅
**Recommendation**: Keep as-is (no API needed for this task)

---

### 4. **Viral Segment Detection** (Audio Analysis)
**Task**: Detect hook segments in audio files

**Current Implementation**: Local audio analysis (Essentia, librosa, madmom)
**Recommendation**: Keep as-is (no API needed - audio processing is done locally)

---

## Model Priority Recommendations

### For Pitch Generation:
```python
# Priority order:
1. GPT-4o Mini (best value)
2. Claude 3.5 Sonnet (best quality, if budget allows)
3. DeepSeek Chat (fallback)
```

### For Lyric Critique:
```python
# Priority order:
1. Claude 3.5 Sonnet (best quality)
2. GPT-4o (good alternative)
3. Gemini 2.0 Flash (cost-sensitive fallback)
```

## Cost Optimization Strategy

1. **Pitch Copy**: Use GPT-4o Mini (90% cost savings vs Claude, similar quality)
2. **Lyric Critique**: Use Claude 3.5 Sonnet (quality matters for critiques)
3. **Tags**: Keep rule-based (free)

## Implementation Notes

- All APIs support OpenAI-compatible format (except Claude uses Anthropic SDK)
- DeepSeek uses OpenAI-compatible API (just change base_url)
- Gemini uses Google's API format (different SDK)
- Perplexity is best for search/research tasks (not needed here)

## Environment Variables Needed

```bash
# Primary (recommended)
OPENAI_API_KEY=sk-...          # GPT-4o Mini for pitch generation
ANTHROPIC_API_KEY=sk-ant-...   # Claude 3.5 Sonnet for lyric critique

# Fallbacks
DEEPSEEK_API_KEY=sk-...        # DeepSeek Chat (very cheap)
GOOGLE_API_KEY=...             # Gemini 2.0 Flash (optional)
```

## Next Steps

1. Update `PitchGenerator` to prioritize GPT-4o Mini
2. Keep `AILyricCritic` on Claude 3.5 Sonnet
3. Add cost tracking to monitor API usage
4. Consider caching for frequently accessed tracks

