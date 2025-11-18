# AI Cost Monitoring System

## Overview

TuneScore includes comprehensive AI cost tracking to monitor spending on AI API calls (Anthropic Claude, OpenAI GPT, etc.). All costs are stored in the `analyses.ai_costs` JSONB column.

## Features

### 1. **Automatic Cost Tracking**
- Costs are recorded per analysis per feature
- Tracks model used, token counts, and timestamp
- Aggregates costs by user, feature, and time period

### 2. **Budget Limits**
Configured in `.env`:
```bash
ANALYSIS_MAX_USD=5.0      # Max cost per single analysis
USER_DAILY_MAX_USD=50.0   # Max cost per user per day
```

### 3. **Monitoring Tools**

#### CLI Tool
Quick command-line monitoring:
```bash
cd backend
source venv/bin/activate
python scripts/monitor_ai_costs.py
```

Output includes:
- Overall statistics (total cost, avg per analysis)
- Cost breakdown by feature
- Cost breakdown by AI model
- Top users by spend
- Recent activity (last 7 days)

#### REST API Endpoints
All endpoints require authentication (Bearer token).

**Get Cost Summary:**
```bash
GET /api/v1/monitoring/ai-costs/summary?days=30
```
Returns:
- Total cost for period
- Costs by feature
- Costs by model
- Average per track

**Get Budget Status:**
```bash
GET /api/v1/monitoring/ai-costs/budget-status
```
Returns:
- Today's spending
- Remaining budget
- Status (ok/warning/over_budget)
- Tracks analyzed today

**Get Daily Breakdown:**
```bash
GET /api/v1/monitoring/ai-costs/daily?days=7
```
Returns:
- Daily cost data
- Date/cost pairs for charting

**Get Per-Track Costs:**
```bash
GET /api/v1/monitoring/ai-costs/tracks?limit=10
```
Returns:
- Cost per track
- Features used
- Sorted by cost (highest first)

## Usage in Code

### Recording Costs

```python
from app.services.ai_cost_tracker import AICostTracker, track_ai_cost

# Method 1: Using the tracker class
cost_info = AICostTracker.calculate_anthropic_cost(
    input_tokens=1500,
    output_tokens=800,
    model="claude-3-5-sonnet-20241022"
)

await AICostTracker.record_cost(
    db=db,
    analysis_id=analysis.id,
    feature="pitch_generation",
    cost=cost_info["cost"],
    model=cost_info["model"],
    tokens=cost_info["tokens"]
)

# Method 2: Convenience function
await track_ai_cost(
    db=db,
    analysis_id=analysis.id,
    feature="lyric_critique",
    cost=0.0025,
    model="claude-3-5-sonnet-20241022",
    tokens={"input": 1200, "output": 500}
)
```

### Cost Calculation Helpers

**For Anthropic (Claude):**
```python
cost_info = AICostTracker.calculate_anthropic_cost(
    input_tokens=1500,
    output_tokens=800,
    model="claude-3-5-sonnet-20241022"
)
# Returns: {'cost': 0.0165, 'model': '...', 'tokens': {...}, 'breakdown': {...}}
```

**For OpenAI (GPT):**
```python
cost_info = AICostTracker.calculate_openai_cost(
    input_tokens=1500,
    output_tokens=800,
    model="gpt-4-turbo"
)
```

### Pricing (as of Nov 2024)

**Anthropic Claude:**
- Claude 3.5 Sonnet: $3/MTok input, $15/MTok output
- Claude 3 Haiku: $0.25/MTok input, $1.25/MTok output
- Claude 3 Opus: $15/MTok input, $75/MTok output

**OpenAI GPT:**
- GPT-4 Turbo: $10/MTok input, $30/MTok output
- GPT-3.5 Turbo: $0.50/MTok input, $1.50/MTok output

## Example Integration

### In your AI service function:

```python
async def generate_pitch_copy(
    analysis_id: int,
    sonic_genome: dict,
    lyrical_genome: dict,
    db: AsyncSession
) -> str:
    """Generate pitch copy using Claude API."""
    
    # Build prompt
    prompt = build_pitch_prompt(sonic_genome, lyrical_genome)
    
    # Call AI API
    message = anthropic_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Calculate and record cost
    cost_info = AICostTracker.calculate_anthropic_cost(
        input_tokens=message.usage.input_tokens,
        output_tokens=message.usage.output_tokens,
        model="claude-3-5-sonnet-20241022"
    )
    
    await track_ai_cost(
        db=db,
        analysis_id=analysis_id,
        feature="pitch_generation",
        cost=cost_info["cost"],
        model=cost_info["model"],
        tokens=cost_info["tokens"]
    )
    
    return message.content[0].text
```

## Database Schema

```sql
-- ai_costs column in analyses table
CREATE TABLE analyses (
    ...
    ai_costs JSONB DEFAULT '{}',
    ...
);

-- Example ai_costs content:
{
  "pitch_generation": {
    "cost": 0.0165,
    "model": "claude-3-5-sonnet-20241022",
    "timestamp": "2025-11-05T12:34:56.789Z",
    "tokens": {
      "input": 1500,
      "output": 800,
      "total": 2300
    },
    "breakdown": {
      "input_cost": 0.0045,
      "output_cost": 0.0120
    }
  },
  "lyric_critique": {
    "cost": 0.0089,
    "model": "claude-3-5-sonnet-20241022",
    "timestamp": "2025-11-05T12:35:12.456Z",
    "tokens": {
      "input": 2100,
      "output": 450
    }
  }
}
```

## Cost Governor

The system includes automatic budget enforcement:

1. **Per-Analysis Limit**: Prevents single expensive operations
2. **Daily User Limit**: Caps total daily spending per user
3. **Status Monitoring**: Real-time budget status via API

Budget violations will:
- Log warnings
- Return errors from API
- Prevent further AI operations until reset

## Monitoring Best Practices

1. **Check Daily**: Run `monitor_ai_costs.py` daily
2. **Set Alerts**: Monitor budget status endpoint
3. **Review Features**: Identify expensive operations
4. **Optimize Prompts**: Reduce token usage where possible
5. **Track Trends**: Use daily breakdown to spot spikes

## API Examples

```bash
# Get your auth token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"your@email.com","password":"yourpass"}' \
  | jq -r '.access_token')

# Get 30-day cost summary
curl -s "http://localhost:8000/api/v1/monitoring/ai-costs/summary?days=30" \
  -H "Authorization: Bearer $TOKEN" | jq

# Check budget status
curl -s "http://localhost:8000/api/v1/monitoring/ai-costs/budget-status" \
  -H "Authorization: Bearer $TOKEN" | jq

# Get daily breakdown
curl -s "http://localhost:8000/api/v1/monitoring/ai-costs/daily?days=7" \
  -H "Authorization: Bearer $TOKEN" | jq

# Get costliest tracks
curl -s "http://localhost:8000/api/v1/monitoring/ai-costs/tracks?limit=10" \
  -H "Authorization: Bearer $TOKEN" | jq
```

## Frontend Integration

The monitoring endpoints are ready for dashboard integration:

```typescript
// Fetch cost summary
const response = await fetch('/api/v1/monitoring/ai-costs/summary?days=30', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const costs = await response.json();

// Display budget status
const budget = await fetch('/api/v1/monitoring/ai-costs/budget-status', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());

console.log(`Today: $${budget.today_spent_usd} / $${budget.daily_limit_usd}`);
console.log(`Status: ${budget.status}`);
```

## Migration Applied

The `ai_costs` column was added via migration:
```bash
alembic revision: 5d8e1eef60bc
Applied: ✓
```

All existing analyses will have `ai_costs = {}` (empty dict).
New analyses will accumulate costs as AI features are used.

