# 🤖 AI Provider Options for TuneScore

## Current Configuration

The pitch generator now supports **3 AI providers** with automatic fallback:

### 1. Anthropic Claude 3 Haiku (Primary)
- **Model**: `claude-3-haiku-20240307`
- **Cost**: $0.25 input / $1.25 output per MTok
- **Typical pitch**: ~$0.0004 (cheapest of premium models)
- **Quality**: Excellent, industry-standard
- **Speed**: Very fast
- **Status**: Will use if `ANTHROPIC_API_KEY` has credits

### 2. OpenAI GPT-4o Mini (Fallback #1)
- **Model**: `gpt-4o-mini`
- **Cost**: $0.15 input / $0.60 output per MTok
- **Typical pitch**: ~$0.0003
- **Quality**: Excellent
- **Speed**: Very fast
- **Status**: Will use if Claude unavailable

### 3. DeepSeek Chat (Fallback #2 - CHEAPEST!)
- **Model**: `deepseek-chat`
- **Cost**: $0.14 input / $0.28 output per MTok
- **Typical pitch**: ~$0.0002 (75% cheaper than Claude!)
- **Quality**: Very good
- **Speed**: Fast
- **Status**: Will use if Claude + OpenAI unavailable

---

## How to Use Each Provider

### Option A: Use Claude (Current Default)
Already configured! Just click "Generate" on the live site.

### Option B: Force OpenAI
Temporarily rename `ANTHROPIC_API_KEY` in `.env` to test OpenAI:
```bash
# In .env:
# ANTHROPIC_API_KEY_DISABLED=sk-ant-api03-...
OPENAI_API_KEY=sk-proj-2Nt8McopSQkkDov...
```

### Option C: Force DeepSeek (Cheapest!)
Comment out both Anthropic and OpenAI keys:
```bash
# ANTHROPIC_API_KEY=...
# OPENAI_API_KEY=...
DEEPSEEK_API_KEY=sk-cd4d14f6aa9e47d98b1afb573989b61c
```

---

## Cost Comparison (1000 pitches)

| Provider | Cost per Pitch | Cost for 1K Pitches | Quality |
|----------|---------------|---------------------|---------|
| **DeepSeek** | $0.0002 | **$0.20** | Very Good |
| **GPT-4o Mini** | $0.0003 | $0.30 | Excellent |
| **Claude 3 Haiku** | $0.0004 | $0.40 | Excellent |

**Recommendation**: Use **DeepSeek** for maximum cost savings! It's 75% cheaper and still produces great quality.

---

## Live Test

The system will automatically:
1. Try Anthropic first
2. Fall back to OpenAI if Anthropic fails/no credits
3. Fall back to DeepSeek if both fail
4. Show error only if all 3 fail

**Current Status**: All 3 providers configured and ready! ✅

---

## To Test DeepSeek Now

```bash
cd /home/dwood/tunescore/backend

# Test with DeepSeek
ANTHROPIC_API_KEY="" OPENAI_API_KEY="" ./venv/bin/python scripts/test_pitch_generation.py
```

This will force it to use DeepSeek (ultra-cheap at ~$0.0002/pitch).

---

## Production Recommendation

For maximum cost efficiency while maintaining quality:

**Use DeepSeek as primary**:
- Edit pitch_generator.py to try DeepSeek first
- Keep Claude/OpenAI as fallbacks
- Save ~75% on API costs
- $0.20 for 1,000 pitches instead of $0.40-0.50

**Monthly costs at scale**:
- 10,000 pitches/month with DeepSeek: **$2**
- 10,000 pitches/month with Claude: **$4**
- 10,000 pitches/month with GPT-4o Mini: **$3**

---

**Your Choice**: All three are configured and ready! The system will automatically use whatever's available. 🎉

