# Feature Brief: AI Lyric Critic & Rewrite Suggestions

**Priority**: 2.7  
**Phase**: 1 (Quick Wins)  
**Effort**: 3/10 (1-2 days)  
**Impact**: 8/10

---

## 🎯 Overview

Use Claude 3.5 Sonnet or GPT-4 to provide actionable feedback on lyrics, suggest rewrites, and improve rhyme schemes. Leverages existing lyrical genome analysis to provide context-aware critiques.

---

## 👥 User Stories

- Creator: "How can I improve my lyrics?"
- Creator: "Suggest alternative rhymes for this line"
- Creator: "Is my verse too repetitive?"
- Creator: "Help me strengthen my chorus"

---

## 🏗️ Architecture

```python
# backend/app/services/lyrics/ai_critic.py

from anthropic import Anthropic
import os

class AILyricCritic:
    """AI-powered lyric critique and rewrite suggestions."""
    
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.max_cost_per_request = 0.10  # Cost governor
    
    def critique(self, lyrics: str, lyrical_genome: dict) -> dict:
        """
        Generate critique and rewrite suggestions.
        
        Args:
            lyrics: Full lyrics text
            lyrical_genome: Existing lyrical analysis from VADER
        
        Returns:
            {
                "overall_critique": "...",
                "strengths": ["...", "..."],
                "weaknesses": ["...", "..."],
                "line_by_line_feedback": [
                    {"line": "...", "feedback": "...", "suggestion": "..."}
                ],
                "alternative_lines": {
                    "verse_1_line_3": ["option1", "option2", "option3"]
                },
                "rhyme_scheme_improvements": ["...", "..."],
                "cost": 0.05
            }
        """
        prompt = self._build_prompt(lyrics, lyrical_genome)
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse response
        critique_data = self._parse_response(response.content[0].text)
        
        # Calculate cost
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        cost = (input_tokens * 0.003 / 1000) + (output_tokens * 0.015 / 1000)
        
        critique_data["cost"] = round(cost, 4)
        
        return critique_data
    
    def _build_prompt(self, lyrics: str, lyrical_genome: dict) -> str:
        """Build critique prompt with context."""
        return f"""You are a professional songwriting coach. Analyze these lyrics and provide constructive feedback.

LYRICS:
{lyrics}

CURRENT ANALYSIS:
- Songwriting Quality: {lyrical_genome.get('songwriting_quality', {}).get('total_score', 'N/A')}/100
- Vocabulary Richness: {lyrical_genome.get('complexity', {}).get('vocabulary_richness', 'N/A')}
- Rhyme Density: {lyrical_genome.get('complexity', {}).get('rhyme_density', 'N/A')}
- Themes: {', '.join(lyrical_genome.get('themes', {}).get('top_themes', []))}
- Sentiment: {lyrical_genome.get('sentiment', {}).get('overall_sentiment', 'N/A')}

Provide:
1. Overall critique (2-3 sentences)
2. Top 3 strengths
3. Top 3 weaknesses
4. Line-by-line feedback for lines that need improvement
5. 3 alternative versions for the weakest lines
6. Rhyme scheme improvement suggestions

Format as JSON with keys: overall_critique, strengths, weaknesses, line_by_line_feedback, alternative_lines, rhyme_scheme_improvements
"""
    
    def _parse_response(self, response_text: str) -> dict:
        """Parse AI response into structured data."""
        import json
        import re
        
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        
        # Fallback: return raw text
        return {
            "overall_critique": response_text,
            "strengths": [],
            "weaknesses": [],
            "line_by_line_feedback": [],
            "alternative_lines": {},
            "rhyme_scheme_improvements": []
        }
```

---

## 🗄️ Database Schema

```python
# Store AI critique in analyses table
class Analysis(Base):
    # ... existing fields ...
    ai_lyric_critique = Column(JSONB, nullable=True)  # NEW FIELD
```

---

## 🌐 API Endpoints

```python
# backend/app/api/routers/tracks.py

@router.post("/tracks/{track_id}/lyric-critique")
async def generate_lyric_critique(
    track_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate AI lyric critique (Creator tier only)."""
    # Check user tier
    if current_user.tier != "creator":
        raise HTTPException(403, "Creator tier required")
    
    # Get track and analysis
    track = await db.get(Track, track_id)
    analysis = await db.get(Analysis, track.analysis_id)
    
    # Generate critique
    critic = AILyricCritic()
    critique = critic.critique(
        track.lyrics,
        analysis.lyrical_genome
    )
    
    # Store in database
    analysis.ai_lyric_critique = critique
    await db.commit()
    
    return critique
```

---

## 🎨 Frontend Component

```svelte
<!-- frontend/src/lib/components/AILyricCritiqueCard.svelte -->

<script lang="ts">
  import { Card, Button, Badge } from '$lib/components/ui';
  
  export let trackId: number;
  let critique: any = null;
  let loading = false;
  
  async function generateCritique() {
    loading = true;
    const response = await fetch(`/api/v1/tracks/${trackId}/lyric-critique`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    critique = await response.json();
    loading = false;
  }
</script>

<Card title="AI Lyric Critique">
  {#if !critique}
    <Button on:click={generateCritique} disabled={loading}>
      {loading ? 'Generating...' : 'Generate AI Critique'}
    </Button>
  {:else}
    <div class="space-y-4">
      <p class="text-gray-700">{critique.overall_critique}</p>
      
      <div>
        <h4 class="font-semibold text-green-600">Strengths</h4>
        <ul class="list-disc list-inside">
          {#each critique.strengths as strength}
            <li>{strength}</li>
          {/each}
        </ul>
      </div>
      
      <div>
        <h4 class="font-semibold text-red-600">Areas for Improvement</h4>
        <ul class="list-disc list-inside">
          {#each critique.weaknesses as weakness}
            <li>{weakness}</li>
          {/each}
        </ul>
      </div>
      
      <!-- Line-by-line feedback, alternatives, etc. -->
    </div>
  {/if}
</Card>
```

---

## 📊 Success Metrics

- Feature usage: >30% of Creator tier users generate critiques
- Engagement: Users spend >2 minutes reading feedback
- Actionability: >20% of users re-upload tracks after critique
- Cost: Average cost per critique <$0.08

---

## 🚀 Implementation Timeline

**Day 1**: Backend integration (AILyricCritic class, API endpoint, cost governor)  
**Day 2**: Frontend component, testing, deployment

---

## 🔒 Cost Management

- Max $0.10 per request (enforced)
- Log all prompts to `logs/ai_prompts.log`
- Monthly budget alerts ($100/month threshold)
- Rate limit: 10 critiques per user per day

