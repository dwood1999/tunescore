"""TuneScore calculation - composite score for track quality and potential."""

from typing import Any


def calculate_tunescore(
    sonic_genome: dict[str, Any],
    lyrical_genome: dict[str, Any] | None,
    hook_data: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Calculate TuneScore (0-100) - a composite score indicating track quality and commercial potential.
    
    Components:
    - Production Quality (30%): Audio clarity, dynamics, mastering
    - Musicality (25%): Harmony, rhythm, structure
    - Lyrical Quality (20%): Complexity, coherence, emotional resonance
    - Hook Potential (15%): Catchiness, memorability
    - Commercial Appeal (10%): Genre fit, market trends
    
    Returns:
        dict with overall score and component breakdowns
    """
    scores = {}
    
    # 1. Production Quality (0-30 points)
    production_score = _calculate_production_quality(sonic_genome)
    scores["production_quality"] = production_score
    
    # 2. Musicality (0-25 points)
    musicality_score = _calculate_musicality(sonic_genome)
    scores["musicality"] = musicality_score
    
    # 3. Lyrical Quality (0-20 points)
    lyrical_score = _calculate_lyrical_quality(lyrical_genome) if lyrical_genome else 10.0
    scores["lyrical_quality"] = lyrical_score
    
    # 4. Hook Potential (0-15 points)
    hook_score = _calculate_hook_potential(hook_data) if hook_data else 7.5
    scores["hook_potential"] = hook_score
    
    # 5. Commercial Appeal (0-10 points)
    commercial_score = _calculate_commercial_appeal(sonic_genome, lyrical_genome)
    scores["commercial_appeal"] = commercial_score
    
    # Calculate total
    total_score = sum(scores.values())
    
    # Determine grade
    grade = _get_grade(total_score)
    
    return {
        "overall_score": round(total_score, 1),
        "grade": grade,
        "components": {
            "production_quality": {
                "score": round(production_score, 1),
                "max": 30,
                "percentage": round((production_score / 30) * 100, 1),
            },
            "musicality": {
                "score": round(musicality_score, 1),
                "max": 25,
                "percentage": round((musicality_score / 25) * 100, 1),
            },
            "lyrical_quality": {
                "score": round(lyrical_score, 1),
                "max": 20,
                "percentage": round((lyrical_score / 20) * 100, 1),
            },
            "hook_potential": {
                "score": round(hook_score, 1),
                "max": 15,
                "percentage": round((hook_score / 15) * 100, 1),
            },
            "commercial_appeal": {
                "score": round(commercial_score, 1),
                "max": 10,
                "percentage": round((commercial_score / 10) * 100, 1),
            },
        },
        "insights": _generate_insights(total_score, scores),
    }


def _calculate_production_quality(sonic_genome: dict[str, Any]) -> float:
    """
    Calculate production quality score (0-30).
    
    Measures audio clarity, mastering quality, and recording fidelity.
    Penalizes poor/amateur recordings.
    """
    score = 0.0
    
    # Dynamic range (RMS variation) - good production has controlled dynamics
    rms_std = sonic_genome.get("rms_std", 0)
    if 0.03 <= rms_std <= 0.08:  # Sweet spot for modern production
        score += 8.0
    elif 0.02 <= rms_std <= 0.10:
        score += 6.0
    else:
        score += 4.0
    
    # Loudness (mastering quality) - penalize quiet/poorly mastered tracks
    loudness = sonic_genome.get("loudness", -20)
    if -14 >= loudness >= -18:  # Modern mastering standards (streaming era)
        score += 8.0
    elif -12 >= loudness >= -20:  # Acceptable range
        score += 6.0
    elif -22 >= loudness >= -25:  # Quiet/amateur (The Shaggs: -22.89)
        score += 3.0
    else:  # Very quiet or very loud (poor mastering)
        score += 2.0
    
    # Spectral balance (frequency distribution)
    spectral_centroid = sonic_genome.get("spectral_centroid_mean", 0)
    if 2000 <= spectral_centroid <= 4000:  # Balanced frequency spectrum
        score += 7.0
    elif 1500 <= spectral_centroid <= 5000:
        score += 5.0
    else:
        score += 3.0
    
    # Zero crossing rate (clarity and transient definition)
    zcr = sonic_genome.get("zero_crossing_rate_mean", 0)
    if 0.08 <= zcr <= 0.15:  # Clear but not harsh
        score += 7.0
    elif 0.05 <= zcr <= 0.20:  # Acceptable
        score += 5.0
    else:  # Too harsh or too muddy
        score += 3.0
    
    return min(score, 30.0)


def _calculate_musicality(sonic_genome: dict[str, Any]) -> float:
    """
    Calculate musicality score (0-25).
    
    This measures technical proficiency, harmonic coherence, and rhythmic consistency.
    Designed to catch issues like The Shaggs - high energy but poor execution.
    """
    score = 0.0
    
    # 1. Spectral Consistency (0-8 points) - measures harmonic coherence
    # Low variance = consistent pitch/harmony, high variance = chaotic/out-of-tune
    spectral_centroid_std = sonic_genome.get("spectral_centroid_std", 1000)
    spectral_centroid_mean = sonic_genome.get("spectral_centroid_mean", 2000)
    
    # Calculate coefficient of variation (normalized variance)
    if spectral_centroid_mean > 0:
        spectral_cv = spectral_centroid_std / spectral_centroid_mean
        
        if spectral_cv < 0.25:  # Very consistent (professional)
            score += 8.0
        elif spectral_cv < 0.35:  # Moderately consistent
            score += 6.0
        elif spectral_cv < 0.50:  # Some inconsistency
            score += 4.0
        else:  # Chaotic (like The Shaggs)
            score += 2.0
    else:
        score += 4.0  # Neutral if we can't calculate
    
    # 2. Rhythmic Stability (0-7 points) - penalize erratic danceability
    # The Shaggs have high "danceability" because librosa misinterprets chaos as rhythm
    danceability = sonic_genome.get("danceability", 0.5)
    energy = sonic_genome.get("energy", 0.5)
    zcr_std = sonic_genome.get("zero_crossing_rate_std", 0.05)
    
    # Detect chaos: extremely high danceability (>0.95) is suspicious
    # Also check if spectral variance suggests inconsistency
    if danceability > 0.95 and spectral_cv > 0.20:
        # Very suspicious - likely chaos (The Shaggs case)
        score += 2.0
    elif danceability > 0.9 and zcr_std > 0.05:
        # Moderately suspicious - high rhythm with high variance
        score += 4.0
    elif danceability > 0.7 and energy > 0.7:
        # Genuinely energetic and rhythmic
        score += 7.0
    elif danceability > 0.5 or energy > 0.5:
        score += 5.0
    else:
        score += 3.0
    
    # 3. Tempo Consistency (0-5 points)
    tempo = sonic_genome.get("tempo", 120)
    if 80 <= tempo <= 160:  # Standard range for most genres
        score += 5.0
    elif 60 <= tempo <= 180:
        score += 3.0
    else:  # Extreme tempos (likely detection error)
        score += 1.0
    
    # 4. Emotional Clarity (0-5 points)
    valence = sonic_genome.get("valence", 0.5)
    # Clear emotional direction (very happy or very sad)
    if valence > 0.7 or valence < 0.3:
        score += 5.0
    else:
        score += 3.0
    
    return min(score, 25.0)


def _calculate_lyrical_quality(lyrical_genome: dict[str, Any]) -> float:
    """Calculate lyrical quality score (0-20)."""
    if not lyrical_genome:
        return 10.0  # Neutral score if no lyrics
    
    score = 0.0
    
    # Vocabulary richness
    complexity = lyrical_genome.get("complexity", {})
    vocab_richness = complexity.get("vocabulary_richness", 0.5)
    if vocab_richness > 0.6:  # Rich vocabulary
        score += 6.0
    elif vocab_richness > 0.4:
        score += 4.0
    else:
        score += 2.0
    
    # Rhyme density
    rhyme_density = complexity.get("rhyme_density", 0)
    if 0.02 <= rhyme_density <= 0.15:  # Good rhyme structure
        score += 5.0
    elif rhyme_density > 0:
        score += 3.0
    else:
        score += 1.0
    
    # Emotional arc (storytelling)
    emotional_arc = lyrical_genome.get("emotional_arc", [])
    if len(emotional_arc) > 10:  # Has emotional progression
        # Calculate variance in sentiment
        compounds = [point.get("compound", 0) for point in emotional_arc]
        if compounds:
            variance = max(compounds) - min(compounds)
            if variance > 0.5:  # Dynamic emotional journey
                score += 5.0
            elif variance > 0.2:
                score += 3.0
            else:
                score += 1.0
    
    # Repetition (catchiness vs. redundancy)
    repetition = lyrical_genome.get("repetition", {})
    rep_score = repetition.get("repetition_score", 0)
    if 2 <= rep_score <= 8:  # Balanced repetition
        score += 4.0
    elif rep_score > 0:
        score += 2.0
    
    return min(score, 20.0)


def _calculate_hook_potential(hook_data: dict[str, Any]) -> float:
    """Calculate hook potential score (0-15)."""
    if not hook_data:
        return 7.5  # Neutral score
    
    hook_score = hook_data.get("hook_score", 0)
    
    # Direct mapping from hook score (0-100) to points (0-15)
    return (hook_score / 100) * 15


def _calculate_commercial_appeal(
    sonic_genome: dict[str, Any],
    lyrical_genome: dict[str, Any] | None,
) -> float:
    """
    Calculate commercial appeal score (0-10).
    
    NOW CONTEXT-AWARE: Considers actual musicianship quality!
    Amateur/chaotic music cannot be commercially viable, regardless of energy.
    """
    score = 0.0
    
    # CRITICAL: Apply quality penalty first
    # Commercial music requires professional execution
    timing_precision = sonic_genome.get("timing_precision_score", 70.0)
    harmonic_coherence = sonic_genome.get("harmonic_coherence_score", 70.0)
    
    # Calculate quality multiplier (0.3 to 1.0)
    # Poor quality (< 50) gets heavily penalized
    avg_quality = (timing_precision + harmonic_coherence) / 2
    
    if avg_quality >= 75:
        quality_multiplier = 1.0  # Professional quality
    elif avg_quality >= 60:
        quality_multiplier = 0.85  # Good quality
    elif avg_quality >= 50:
        quality_multiplier = 0.65  # Acceptable
    elif avg_quality >= 40:
        quality_multiplier = 0.45  # Poor quality (The Shaggs territory)
    else:
        quality_multiplier = 0.30  # Amateur/unusable
    
    # Duration (radio-friendly length)
    duration = sonic_genome.get("duration", 0)
    if 150 <= duration <= 240:  # 2:30 - 4:00 (radio sweet spot)
        score += 3.0
    elif 120 <= duration <= 300:  # 2:00 - 5:00
        score += 2.0
    else:
        score += 1.0
    
    # Energy (commercial tracks tend to be energetic)
    # BUT: energy without quality is chaos, not commercial appeal
    energy = sonic_genome.get("energy", 0.5)
    if energy > 0.6:
        score += 3.0
    elif energy > 0.4:
        score += 2.0
    else:
        score += 1.0
    
    # Danceability (context-aware version)
    # The new danceability already considers timing precision!
    danceability = sonic_genome.get("danceability", 0.5)
    if danceability > 0.7:
        score += 2.0
    elif danceability > 0.5:
        score += 1.5
    else:
        score += 0.5
    
    # Lyrical themes (if available)
    if lyrical_genome:
        themes = lyrical_genome.get("themes", [])
        commercial_themes = {"love", "party", "success", "money", "celebration"}
        if any(theme in commercial_themes for theme in themes):
            score += 2.0
        else:
            score += 1.0
    else:
        score += 1.0
    
    # Apply quality multiplier - KEY CHANGE!
    # The Shaggs: base score ~9, multiplier ~0.45 = final score ~4.0
    # Professional: base score ~10, multiplier ~1.0 = final score ~10.0
    final_score = score * quality_multiplier
    
    return min(final_score, 10.0)


def _get_grade(score: float) -> str:
    """Convert score to letter grade."""
    if score >= 90:
        return "A+"
    elif score >= 85:
        return "A"
    elif score >= 80:
        return "A-"
    elif score >= 75:
        return "B+"
    elif score >= 70:
        return "B"
    elif score >= 65:
        return "B-"
    elif score >= 60:
        return "C+"
    elif score >= 55:
        return "C"
    elif score >= 50:
        return "C-"
    elif score >= 45:
        return "D+"
    elif score >= 40:
        return "D"
    else:
        return "F"


def _generate_insights(total_score: float, component_scores: dict[str, float]) -> list[str]:
    """Generate actionable insights based on scores."""
    insights = []
    
    # Overall assessment
    if total_score >= 80:
        insights.append("🎯 Exceptional track with strong commercial potential")
    elif total_score >= 70:
        insights.append("✨ Solid track with good market viability")
    elif total_score >= 60:
        insights.append("💡 Promising foundation, some areas need refinement")
    else:
        insights.append("🔧 Significant improvements needed for commercial release")
    
    # Component-specific insights
    if component_scores["production_quality"] < 20:
        insights.append("🎚️ Consider professional mixing/mastering to enhance production quality")
    
    if component_scores["musicality"] < 15:
        insights.append("🎵 Work on musical arrangement and energy dynamics")
    
    if component_scores["lyrical_quality"] < 12:
        insights.append("✍️ Enhance lyrical depth and storytelling")
    
    if component_scores["hook_potential"] < 10:
        insights.append("🎣 Strengthen the hook to improve memorability")
    
    if component_scores["commercial_appeal"] < 6:
        insights.append("📊 Consider market trends and radio-friendly elements")
    
    # Strengths
    max_component = max(component_scores.items(), key=lambda x: x[1])
    if max_component[1] > 20:
        component_names = {
            "production_quality": "production quality",
            "musicality": "musicality",
            "lyrical_quality": "lyrical content",
            "hook_potential": "hook",
            "commercial_appeal": "commercial appeal",
        }
        insights.append(f"💪 Strongest area: {component_names.get(max_component[0], max_component[0])}")
    
    return insights

