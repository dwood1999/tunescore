"""Artist similarity calculation based on sonic and lyrical fingerprints."""

from typing import Any

import numpy as np


def calculate_artist_similarity(
    artist1_tracks: list[dict[str, Any]],
    artist2_tracks: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Calculate similarity between two artists based on their tracks.
    
    Args:
        artist1_tracks: List of track data (sonic_genome, lyrical_genome) for artist 1
        artist2_tracks: List of track data (sonic_genome, lyrical_genome) for artist 2
    
    Returns:
        dict with overall similarity score and component breakdowns
    """
    if not artist1_tracks or not artist2_tracks:
        return {
            "overall_similarity": 0.0,
            "sonic_similarity": 0.0,
            "lyrical_similarity": 0.0,
            "style_match": "insufficient_data",
        }
    
    # Calculate average sonic fingerprint for each artist
    artist1_sonic = _aggregate_sonic_features(artist1_tracks)
    artist2_sonic = _aggregate_sonic_features(artist2_tracks)
    
    # Calculate average lyrical fingerprint for each artist
    artist1_lyrical = _aggregate_lyrical_features(artist1_tracks)
    artist2_lyrical = _aggregate_lyrical_features(artist2_tracks)
    
    # Calculate sonic similarity (0-100)
    sonic_similarity = _calculate_sonic_similarity(artist1_sonic, artist2_sonic)
    
    # Calculate lyrical similarity (0-100)
    lyrical_similarity = _calculate_lyrical_similarity(artist1_lyrical, artist2_lyrical)
    
    # Overall similarity (weighted average)
    overall_similarity = (sonic_similarity * 0.6) + (lyrical_similarity * 0.4)
    
    # Determine style match category
    style_match = _categorize_similarity(overall_similarity)
    
    return {
        "overall_similarity": round(overall_similarity, 1),
        "sonic_similarity": round(sonic_similarity, 1),
        "lyrical_similarity": round(lyrical_similarity, 1),
        "style_match": style_match,
        "sonic_breakdown": _get_sonic_breakdown(artist1_sonic, artist2_sonic),
        "lyrical_breakdown": _get_lyrical_breakdown(artist1_lyrical, artist2_lyrical),
    }


def _aggregate_sonic_features(tracks: list[dict[str, Any]]) -> dict[str, float]:
    """Aggregate sonic features across multiple tracks."""
    features = {
        "tempo": [],
        "energy": [],
        "danceability": [],
        "valence": [],
        "acousticness": [],
        "loudness": [],
        "spectral_centroid_mean": [],
    }
    
    for track in tracks:
        sonic = track.get("sonic_genome", {})
        for key in features:
            if key in sonic:
                features[key].append(sonic[key])
    
    # Calculate averages
    return {key: np.mean(values) if values else 0.0 for key, values in features.items()}


def _aggregate_lyrical_features(tracks: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate lyrical features across multiple tracks."""
    vocab_richness = []
    rhyme_density = []
    avg_line_length = []
    themes = []
    
    for track in tracks:
        lyrical = track.get("lyrical_genome", {})
        if not lyrical:
            continue
        
        complexity = lyrical.get("complexity", {})
        if "vocabulary_richness" in complexity:
            vocab_richness.append(complexity["vocabulary_richness"])
        if "rhyme_density" in complexity:
            rhyme_density.append(complexity["rhyme_density"])
        if "avg_line_length" in complexity:
            avg_line_length.append(complexity["avg_line_length"])
        
        track_themes = lyrical.get("themes", [])
        themes.extend(track_themes)
    
    return {
        "vocabulary_richness": np.mean(vocab_richness) if vocab_richness else 0.0,
        "rhyme_density": np.mean(rhyme_density) if rhyme_density else 0.0,
        "avg_line_length": np.mean(avg_line_length) if avg_line_length else 0.0,
        "common_themes": list(set(themes)),
    }


def _calculate_sonic_similarity(artist1: dict[str, float], artist2: dict[str, float]) -> float:
    """
    Calculate sonic similarity between two artists (0-100).
    
    Uses weighted distance metrics for each feature.
    """
    weights = {
        "tempo": 0.15,
        "energy": 0.20,
        "danceability": 0.20,
        "valence": 0.15,
        "acousticness": 0.15,
        "loudness": 0.10,
        "spectral_centroid_mean": 0.05,
    }
    
    total_similarity = 0.0
    
    for feature, weight in weights.items():
        val1 = artist1.get(feature, 0)
        val2 = artist2.get(feature, 0)
        
        # Normalize based on feature type
        if feature == "tempo":
            # Tempo: 0-200 BPM range
            max_diff = 200
            diff = abs(val1 - val2)
        elif feature == "loudness":
            # Loudness: -60 to 0 dB range
            max_diff = 60
            diff = abs(val1 - val2)
        elif feature == "spectral_centroid_mean":
            # Spectral centroid: 0-8000 Hz range
            max_diff = 8000
            diff = abs(val1 - val2)
        else:
            # Normalized features (0-1)
            max_diff = 1.0
            diff = abs(val1 - val2)
        
        # Convert difference to similarity (0-1)
        similarity = 1.0 - min(diff / max_diff, 1.0)
        total_similarity += similarity * weight
    
    return total_similarity * 100


def _calculate_lyrical_similarity(artist1: dict[str, Any], artist2: dict[str, Any]) -> float:
    """Calculate lyrical similarity between two artists (0-100)."""
    similarity_score = 0.0
    
    # Vocabulary richness similarity (0-30 points)
    vocab1 = artist1.get("vocabulary_richness", 0)
    vocab2 = artist2.get("vocabulary_richness", 0)
    vocab_diff = abs(vocab1 - vocab2)
    vocab_similarity = (1.0 - min(vocab_diff, 1.0)) * 30
    similarity_score += vocab_similarity
    
    # Rhyme density similarity (0-25 points)
    rhyme1 = artist1.get("rhyme_density", 0)
    rhyme2 = artist2.get("rhyme_density", 0)
    rhyme_diff = abs(rhyme1 - rhyme2)
    rhyme_similarity = (1.0 - min(rhyme_diff, 1.0)) * 25
    similarity_score += rhyme_similarity
    
    # Line length similarity (0-20 points)
    line1 = artist1.get("avg_line_length", 0)
    line2 = artist2.get("avg_line_length", 0)
    line_diff = abs(line1 - line2)
    line_similarity = (1.0 - min(line_diff / 20, 1.0)) * 20
    similarity_score += line_similarity
    
    # Theme overlap (0-25 points)
    themes1 = set(artist1.get("common_themes", []))
    themes2 = set(artist2.get("common_themes", []))
    if themes1 and themes2:
        overlap = len(themes1 & themes2) / len(themes1 | themes2)
        theme_similarity = overlap * 25
    else:
        theme_similarity = 0
    similarity_score += theme_similarity
    
    return similarity_score


def _categorize_similarity(score: float) -> str:
    """Categorize similarity score into descriptive labels."""
    if score >= 85:
        return "nearly_identical"
    elif score >= 70:
        return "very_similar"
    elif score >= 55:
        return "similar"
    elif score >= 40:
        return "somewhat_similar"
    else:
        return "different"


def _get_sonic_breakdown(artist1: dict[str, float], artist2: dict[str, float]) -> dict[str, Any]:
    """Get detailed sonic feature comparison."""
    return {
        "tempo": {
            "artist1": round(artist1.get("tempo", 0), 1),
            "artist2": round(artist2.get("tempo", 0), 1),
            "difference": round(abs(artist1.get("tempo", 0) - artist2.get("tempo", 0)), 1),
        },
        "energy": {
            "artist1": round(artist1.get("energy", 0), 2),
            "artist2": round(artist2.get("energy", 0), 2),
            "difference": round(abs(artist1.get("energy", 0) - artist2.get("energy", 0)), 2),
        },
        "danceability": {
            "artist1": round(artist1.get("danceability", 0), 2),
            "artist2": round(artist2.get("danceability", 0), 2),
            "difference": round(abs(artist1.get("danceability", 0) - artist2.get("danceability", 0)), 2),
        },
        "valence": {
            "artist1": round(artist1.get("valence", 0), 2),
            "artist2": round(artist2.get("valence", 0), 2),
            "difference": round(abs(artist1.get("valence", 0) - artist2.get("valence", 0)), 2),
        },
    }


def _get_lyrical_breakdown(artist1: dict[str, Any], artist2: dict[str, Any]) -> dict[str, Any]:
    """Get detailed lyrical feature comparison."""
    themes1 = set(artist1.get("common_themes", []))
    themes2 = set(artist2.get("common_themes", []))
    
    return {
        "vocabulary_richness": {
            "artist1": round(artist1.get("vocabulary_richness", 0), 3),
            "artist2": round(artist2.get("vocabulary_richness", 0), 3),
            "difference": round(abs(artist1.get("vocabulary_richness", 0) - artist2.get("vocabulary_richness", 0)), 3),
        },
        "rhyme_density": {
            "artist1": round(artist1.get("rhyme_density", 0), 3),
            "artist2": round(artist2.get("rhyme_density", 0), 3),
            "difference": round(abs(artist1.get("rhyme_density", 0) - artist2.get("rhyme_density", 0)), 3),
        },
        "shared_themes": list(themes1 & themes2),
        "unique_to_artist1": list(themes1 - themes2),
        "unique_to_artist2": list(themes2 - themes1),
    }

