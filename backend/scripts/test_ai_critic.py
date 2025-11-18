#!/usr/bin/env python3
"""
Test AI Lyric Critic.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.lyrics.ai_critic import AILyricCritic

print("=" * 60)
print("AI LYRIC CRITIC - TEST")
print("=" * 60)
print()

# Sample lyrics for testing
sample_lyrics = """[Verse 1]
Walking down the street today
Sun is shining bright
Everything feels right
Nothing in my way

[Chorus]
Life is good, life is great
Never gonna hesitate
Living for today
That's the only way

[Verse 2]
People passing by me now
Smiling all around
Happiness I found
Don't know why or how"""

# Mock lyrical genome
mock_genome = {
    "songwriting_quality": {
        "total_score": 65,
        "grade": "C+",
    },
    "complexity": {
        "vocabulary_richness": 0.45,
        "rhyme_density": 0.6,
    },
    "themes": {
        "top_themes": ["happiness", "living in the moment"],
    },
    "sentiment": {
        "overall_sentiment": "positive",
    },
}

print("Sample Lyrics:")
print(sample_lyrics)
print()
print("=" * 60)
print()

# Test AI Critic
try:
    critic = AILyricCritic()
    print("✅ AILyricCritic initialized")
    print()
    
    print("Generating critique...")
    print("(This may take 5-10 seconds)")
    print()
    
    result = critic.critique(sample_lyrics, mock_genome)
    
    if "error" in result and result["error"]:
        print(f"❌ Error: {result['error']}")
    else:
        print("✅ CRITIQUE GENERATED")
        print()
        print(f"Cost: ${result['cost']:.4f}")
        print(f"Tokens: {result.get('tokens', {})}")
        print()
        print("Overall Critique:")
        print(f"  {result['overall_critique']}")
        print()
        
        if result.get('strengths'):
            print("Strengths:")
            for i, strength in enumerate(result['strengths'], 1):
                print(f"  {i}. {strength}")
            print()
        
        if result.get('weaknesses'):
            print("Areas for Improvement:")
            for i, weakness in enumerate(result['weaknesses'], 1):
                print(f"  {i}. {weakness}")
            print()
        
        if result.get('line_by_line_feedback'):
            print("Line-by-Line Feedback (first 3):")
            for feedback in result['line_by_line_feedback'][:3]:
                print(f"  Line {feedback.get('line_number', '?')}: {feedback.get('original_line', '')}")
                print(f"    Feedback: {feedback.get('feedback', '')}")
                if feedback.get('suggestion'):
                    print(f"    Suggestion: {feedback.get('suggestion')}")
            print()
        
        if result.get('alternative_lines'):
            print("Alternative Lines:")
            for line_ref, alternatives in list(result['alternative_lines'].items())[:2]:
                print(f"  {line_ref}:")
                for alt in alternatives:
                    print(f"    - {alt}")
            print()
        
        if result.get('rhyme_scheme_improvements'):
            print("Rhyme Scheme Improvements:")
            for i, improvement in enumerate(result['rhyme_scheme_improvements'], 1):
                print(f"  {i}. {improvement}")
            print()
    
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print()
    print("Check logs/ai_prompts.log for detailed logging")

except ValueError as e:
    print(f"❌ Configuration Error: {e}")
    print()
    print("Make sure ANTHROPIC_API_KEY is set in .env file")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

