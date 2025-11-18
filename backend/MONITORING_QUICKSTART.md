# AI Cost Monitoring - Quick Start Guide

## ✅ What's Been Set Up

1. **Database Column**: `analyses.ai_costs` (JSONB) - stores all AI costs
2. **API Endpoints**: 4 monitoring endpoints under `/api/v1/monitoring/`
3. **CLI Tool**: `scripts/monitor_ai_costs.py` for quick terminal checks
4. **Cost Tracker**: Utility functions to calculate and record costs
5. **Documentation**: `AI_COST_MONITORING.md` with full details

## 🚀 Quick Commands

### Check Costs (CLI)
```bash
cd /home/dwood/tunescore/backend
source venv/bin/activate
python scripts/monitor_ai_costs.py
```

### Check Costs (API)
```bash
# Login first
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"your@email.com","password":"yourpass"}' \
  | jq -r '.access_token')

# Get summary
curl -s "http://localhost:8000/api/v1/monitoring/ai-costs/summary?days=30" \
  -H "Authorization: Bearer $TOKEN" | jq

# Check budget
curl -s "http://localhost:8000/api/v1/monitoring/ai-costs/budget-status" \
  -H "Authorization: Bearer $TOKEN" | jq
```

## 📊 Available Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/monitoring/ai-costs/summary?days=N` | Overall cost summary |
| `GET /api/v1/monitoring/ai-costs/daily?days=N` | Daily breakdown |
| `GET /api/v1/monitoring/ai-costs/tracks?limit=N` | Per-track costs |
| `GET /api/v1/monitoring/ai-costs/budget-status` | Budget status |

All require Bearer token authentication.

## 💰 Budget Limits (in .env)

```bash
ANALYSIS_MAX_USD=5.0      # Max per analysis
USER_DAILY_MAX_USD=50.0   # Max per user per day
```

## 📝 Example: Recording Costs in Code

```python
from app.services.ai_cost_tracker import track_ai_cost, AICostTracker

# After calling AI API:
cost_info = AICostTracker.calculate_anthropic_cost(
    input_tokens=message.usage.input_tokens,
    output_tokens=message.usage.output_tokens,
    model="claude-3-5-sonnet-20241022"
)

await track_ai_cost(
    db=db,
    analysis_id=analysis.id,
    feature="pitch_generation",  # or "lyric_critique", etc.
    cost=cost_info["cost"],
    model=cost_info["model"],
    tokens=cost_info["tokens"]
)
```

## 🎯 What It Tracks

- ✅ Total cost per analysis
- ✅ Cost per feature (pitch, critique, etc.)
- ✅ Cost per AI model
- ✅ Token usage (input/output)
- ✅ Daily spending per user
- ✅ Budget status and alerts

## 📈 Current Status

Run the CLI tool to see:
- Overall statistics
- Cost by feature
- Cost by AI model  
- Top users by spend
- Last 7 days activity

## 🔗 More Info

See `AI_COST_MONITORING.md` for complete documentation.
