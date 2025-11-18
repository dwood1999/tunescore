"""Genre detection from audio features and lyrics."""

from typing import Any

HF_TO_CANONICAL = {
    "hiphop": "Hip-Hop/Rap",
    "hip-hop": "Hip-Hop/Rap",
    "metal": "Metal",
    "pop": "Pop",
    "country": "Country",
    "rock": "Rock",
    "classical": "Classical/Instrumental",
    "instrumental": "Classical/Instrumental",
    "reggae": "Reggae/Dancehall",
    "dancehall": "Reggae/Dancehall",
    "jazz": "Jazz/Blues",
    "blues": "Jazz/Blues",
    "disco": "Electronic/EDM",
    "electronic": "Electronic/EDM",
}


def detect_genre(
    sonic_genome: dict[str, Any],
    lyrical_genome: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Detect music genre from audio features and lyrics.
    
    Returns top 3 genre predictions with confidence scores.
    """
    genre_scores = {}
    
    # Extract key features
    tempo = sonic_genome.get("tempo", 120)
    energy = sonic_genome.get("energy", 0.5)
    danceability = sonic_genome.get("danceability", 0.5)
    valence = sonic_genome.get("valence", 0.5)
    acousticness = sonic_genome.get("acousticness", 0.5)
    loudness = sonic_genome.get("loudness", -10)
    spectral_centroid = sonic_genome.get("spectral_centroid_mean", 3000)
    
    # Lyrical features (if available)
    themes = []
    vocab_richness = 0.5
    if lyrical_genome:
        themes = lyrical_genome.get("themes", [])
        complexity = lyrical_genome.get("complexity", {})
        vocab_richness = complexity.get("vocabulary_richness", 0.5)
    
    # Genre detection rules (simplified heuristic classifier)
    # In production, this would be a trained ML model
    
    # Electronic/EDM
    edm_score = 0
    if tempo > 120 and danceability > 0.7 and energy > 0.7:
        edm_score += 40
    if acousticness < 0.3:
        edm_score += 30
    if any(theme in ["party", "club", "dance"] for theme in themes):
        edm_score += 20
    if spectral_centroid > 3500:
        edm_score += 10
    genre_scores["Electronic/EDM"] = min(edm_score, 100)
    
    # Hip-Hop/Rap
    hiphop_score = 0
    # Modern hip-hop can range from slow (80) to fast (140+)
    if 80 <= tempo <= 140:
        hiphop_score += 30
    elif tempo > 140:  # Fast rap/trap
        hiphop_score += 20
    # Hip-hop often has high energy, but danceability varies
    if energy > 0.7:
        hiphop_score += 25
    if danceability > 0.4:  # More flexible danceability
        hiphop_score += 15
    if vocab_richness > 0.6:  # Complex lyrics
        hiphop_score += 25
    elif vocab_richness > 0.2:  # Some hip-hop has simpler/repetitive lyrics
        hiphop_score += 10
    if any(theme in ["money", "success", "struggle", "party", "social_commentary"] for theme in themes):
        hiphop_score += 15
    if acousticness < 0.4:  # Electronic/produced sound
        hiphop_score += 10
    genre_scores["Hip-Hop/Rap"] = min(hiphop_score, 100)
    
    # Pop
    pop_score = 0
    if 100 <= tempo <= 130:
        pop_score += 30
    if 0.5 <= energy <= 0.8 and 0.5 <= danceability <= 0.9:
        pop_score += 30
    if valence > 0.5:  # Generally positive
        pop_score += 20
    if any(theme in ["love", "party", "celebration"] for theme in themes):
        pop_score += 15
    if -12 >= loudness >= -8:  # Modern pop mastering
        pop_score += 5
    genre_scores["Pop"] = min(pop_score, 100)
    
    # Rock
    rock_score = 0
    if 100 <= tempo <= 140:
        rock_score += 25
    if energy > 0.7:
        rock_score += 30
    if 0.3 <= acousticness <= 0.6:  # Mix of acoustic and electric
        rock_score += 25
    if spectral_centroid > 2500:  # Bright, guitar-heavy
        rock_score += 15
    if any(theme in ["rebellion", "freedom", "introspection"] for theme in themes):
        rock_score += 5
    genre_scores["Rock"] = min(rock_score, 100)
    
    # R&B/Soul
    rnb_score = 0
    if 70 <= tempo <= 110:
        rnb_score += 30
    if 0.4 <= energy <= 0.7 and danceability > 0.5:
        rnb_score += 25
    if valence > 0.4:
        rnb_score += 20
    if any(theme in ["love", "romance", "heartbreak"] for theme in themes):
        rnb_score += 20
    if acousticness > 0.3:
        rnb_score += 5
    genre_scores["R&B/Soul"] = min(rnb_score, 100)
    
    # Country
    country_score = 0
    if 90 <= tempo <= 130:
        country_score += 25
    if acousticness > 0.5:
        country_score += 35
    if valence > 0.4:
        country_score += 20
    if any(theme in ["nostalgia", "home", "love", "heartbreak"] for theme in themes):
        country_score += 15
    if spectral_centroid < 3000:
        country_score += 5
    genre_scores["Country"] = min(country_score, 100)
    
    # Indie/Alternative
    indie_score = 0
    if 90 <= tempo <= 130:
        indie_score += 20
    if 0.4 <= energy <= 0.7:
        indie_score += 25
    if 0.3 <= acousticness <= 0.7:
        indie_score += 25
    if vocab_richness > 0.55:  # Thoughtful lyrics
        indie_score += 20
    if any(theme in ["introspection", "nostalgia", "melancholy"] for theme in themes):
        indie_score += 10
    genre_scores["Indie/Alternative"] = min(indie_score, 100)
    
    # Jazz/Blues
    jazz_score = 0
    if 60 <= tempo <= 120:
        jazz_score += 20
    if acousticness > 0.6:
        jazz_score += 30
    if energy < 0.6:
        jazz_score += 20
    if spectral_centroid > 2000 and spectral_centroid < 3500:
        jazz_score += 20
    if valence < 0.5:  # Often melancholic
        jazz_score += 10
    genre_scores["Jazz/Blues"] = min(jazz_score, 100)
    
    # Classical/Instrumental
    classical_score = 0
    if acousticness > 0.8:
        classical_score += 50
    if energy < 0.5:
        classical_score += 20
    if danceability < 0.5:
        classical_score += 20
    if not themes:  # Instrumental
        classical_score += 10
    genre_scores["Classical/Instrumental"] = min(classical_score, 100)
    
    # Reggae/Dancehall
    reggae_score = 0
    if 60 <= tempo <= 90:
        reggae_score += 30
    if danceability > 0.7:
        reggae_score += 30
    if 0.4 <= energy <= 0.7:
        reggae_score += 20
    if any(theme in ["freedom", "love", "party"] for theme in themes):
        reggae_score += 15
    if valence > 0.5:
        reggae_score += 5
    genre_scores["Reggae/Dancehall"] = min(reggae_score, 100)
    
    # Metal
    metal_score = 0
    if tempo > 130 or tempo < 80:  # Very fast or very slow
        metal_score += 20
    if energy > 0.8:
        metal_score += 35
    if loudness > -8:  # Very loud
        metal_score += 20
    if spectral_centroid > 3500:  # Bright, distorted
        metal_score += 15
    if acousticness < 0.2:
        metal_score += 10
    genre_scores["Metal"] = min(metal_score, 100)
    
    # Sort by confidence and get top 3
    sorted_genres = sorted(genre_scores.items(), key=lambda x: x[1], reverse=True)
    top_genres = sorted_genres[:3]
    
    # Normalize to percentages
    total_score = sum(score for _, score in top_genres)
    if total_score > 0:
        predictions = [
            {
                "genre": genre,
                "confidence": round((score / total_score) * 100, 1),
                "raw_score": score,
            }
            for genre, score in top_genres
            if score > 0
        ]
    else:
        predictions = [{"genre": "Unknown", "confidence": 100.0, "raw_score": 0}]
    
    return {
        "primary_genre": predictions[0]["genre"] if predictions else "Unknown",
        "confidence": predictions[0]["confidence"] if predictions else 0.0,
        "predictions": predictions,
        "all_scores": {genre: score for genre, score in sorted_genres if score > 0},
    }


def detect_genre_hybrid(
    audio_path: str | None,
    sonic_genome: dict[str, Any],
    lyrical_genome: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Blend ML genre prediction, instrument detection and heuristic scores."""
    # Start with the heuristic baseline
    heuristic_result = detect_genre(sonic_genome, lyrical_genome)

    if not audio_path:
        return heuristic_result

    # Lazy imports to avoid heavy dependencies when unused
    try:
        from app.services.classification.genre_ml import classify_file, to_score_map
        from app.services.audio.instrument_detection import detect_instruments
        import librosa
    except Exception:
        # Required dependencies missing; fall back to heuristic
        return heuristic_result

    ml_scores_normalized: dict[str, float] = {}
    ml_metadata: dict[str, Any] = {}
    instrument_scores: dict[str, float] = {}
    instrument_debug: dict[str, Any] = {}

    try:
        ml_results = classify_file(audio_path, top_k=10)
        raw_ml_scores = to_score_map(ml_results)
        canonical_scores: dict[str, float] = {}
        for label, score in raw_ml_scores.items():
            canonical = HF_TO_CANONICAL.get(label, label.title())
            canonical_scores[canonical] = canonical_scores.get(canonical, 0.0) + score
        total_ml = sum(canonical_scores.values()) or 1.0
        ml_scores_normalized = {genre: score / total_ml for genre, score in canonical_scores.items()}
        ml_metadata = {
            "raw_predictions": ml_results,
            "canonical_scores": canonical_scores,
        }
    except Exception as exc:  # pragma: no cover - best effort
        ml_metadata = {"error": str(exc)}

    try:
        audio, sr = librosa.load(str(audio_path), sr=16000, duration=30)
        instrument_debug = detect_instruments(audio, sr)
        instrument_scores = instrument_debug.get("instruments", {})
    except Exception as exc:  # pragma: no cover - best effort
        instrument_debug = {"error": str(exc), "instruments": {}}

    heuristic_scores = heuristic_result.get("all_scores", {})
    heuristic_total = sum(heuristic_scores.values()) or 1.0
    heuristic_normalized = {
        genre: score / heuristic_total for genre, score in heuristic_scores.items()
    }

    # Instrument-driven boosts
    boosts: dict[str, float] = {}
    violin_score = instrument_scores.get("violin", 0.0)
    if violin_score > 0.01:
        boosts["Country"] = boosts.get("Country", 0.0) + 4.0 * violin_score
        boosts["Bluegrass"] = boosts.get("Bluegrass", 0.0) + 3.0 * violin_score
        boosts["Folk"] = boosts.get("Folk", 0.0) + 1.5 * violin_score

    acoustic_score = instrument_scores.get("acoustic_guitar", 0.0)
    if acoustic_score > 0.005:
        boosts["Country"] = boosts.get("Country", 0.0) + 1.5 * acoustic_score
        boosts["Folk"] = boosts.get("Folk", 0.0) + 0.8 * acoustic_score

    harmonica_score = instrument_scores.get("harmonica", 0.0)
    if harmonica_score > 0.003:
        boosts["Country"] = boosts.get("Country", 0.0) + 1.0 * harmonica_score
        boosts["Jazz/Blues"] = boosts.get("Jazz/Blues", 0.0) + 0.7 * harmonica_score

    drum_score = instrument_scores.get("drums", 0.0)
    if drum_score > 0.005:
        boosts["Rock"] = boosts.get("Rock", 0.0) + 0.4 * drum_score

    # Combine scores (weights tuned experimentally)
    ml_weight = 0.2
    heuristic_weight = 0.2

    final_scores: dict[str, float] = {}
    genres = set(list(heuristic_normalized.keys()) + list(ml_scores_normalized.keys()) + list(boosts.keys()))
    for genre in genres:
        score = (
            ml_scores_normalized.get(genre, 0.0) * ml_weight
            + heuristic_normalized.get(genre, 0.0) * heuristic_weight
            + boosts.get(genre, 0.0)
        )
        final_scores[genre] = score

    if not final_scores:
        return heuristic_result

    total_final = sum(final_scores.values()) or 1.0
    normalized_final = {genre: score / total_final for genre, score in final_scores.items()}
    sorted_final = sorted(normalized_final.items(), key=lambda x: x[1], reverse=True)
    top_final = sorted_final[:3]

    predictions = [
        {
            "genre": genre,
            "confidence": round(score * 100, 1),
            "raw_score": round(final_scores[genre] * 100, 2),
        }
        for genre, score in top_final
    ]

    return {
        "primary_genre": predictions[0]["genre"] if predictions else heuristic_result.get("primary_genre", "Unknown"),
        "confidence": predictions[0]["confidence"] if predictions else heuristic_result.get("confidence", 0.0),
        "predictions": predictions,
        "all_scores": {genre: round(score * 100, 2) for genre, score in sorted_final},
        "method": "hybrid_ml_instrument",
        "components": {
            "heuristic": heuristic_scores,
            "ml": ml_metadata,
            "instruments": instrument_debug,
        },
    }

