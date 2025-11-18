"""Breakout prediction scorer using RandomForest + XGBoost ensemble.

Predicts track/artist breakout potential using ML models trained on
historical success patterns.
"""

import logging
import os
from datetime import date
from typing import Any

import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Try to import ML libraries
ML_AVAILABLE = False
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    import xgboost as xgb
    import joblib

    ML_AVAILABLE = True
    logger.info("✅ ML libraries loaded for breakout scoring")
except ImportError:
    logger.warning("⚠️ sklearn/xgboost not available - breakout scoring disabled")


class BreakoutScorer:
    """
    Predict breakout potential using ensemble ML model.

    Combines:
    - Velocity metrics (7d/28d growth)
    - TuneScore quality indicators
    - Playlist momentum
    - Social signals
    - Sonic features
    """

    MODEL_PATH = "models/breakout_predictor.pkl"
    SCALER_PATH = "models/breakout_scaler.pkl"

    def __init__(self) -> None:
        """Initialize breakout scorer."""
        self.available = ML_AVAILABLE
        self.model = None
        self.scaler = None

        if ML_AVAILABLE:
            self._load_or_create_model()

    def _load_or_create_model(self) -> None:
        """Load existing model or create new one."""
        if os.path.exists(self.MODEL_PATH) and os.path.exists(self.SCALER_PATH):
            try:
                self.model = joblib.load(self.MODEL_PATH)
                self.scaler = joblib.load(self.SCALER_PATH)
                logger.info("✅ Loaded pre-trained breakout model")
            except Exception as e:
                logger.warning(f"Failed to load model: {e}, creating new one")
                self._create_default_model()
        else:
            self._create_default_model()

    def _create_default_model(self) -> None:
        """Create a default ensemble model."""
        # Create ensemble: RandomForest + XGBoost
        # RandomForest for feature importance + robustness
        # XGBoost for gradient boosting power
        
        self.rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
        )
        
        self.xgb_model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
        )
        
        self.scaler = StandardScaler()
        
        # Note: Model needs to be trained on historical data
        # For now, using rule-based scoring with ML structure
        logger.info("✅ Created default ensemble model (needs training)")

    def predict_breakout(
        self,
        track_data: dict[str, Any],
        artist_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Predict breakout potential for a track.

        Args:
            track_data: Track features and metrics
            artist_data: Optional artist metrics

        Returns:
            Breakout prediction with score, confidence, and factors
        """
        if not self.available:
            return {
                "available": False,
                "breakout_score": 0,
                "confidence": 0,
            }

        # Extract features
        features = self._extract_features(track_data, artist_data)

        # For now, use rule-based scoring until model is trained
        # In production, this would use: self.model.predict_proba(features)
        score, confidence, factors = self._rule_based_scoring(features, track_data, artist_data)

        return {
            "available": True,
            "breakout_score": int(score),
            "confidence": round(confidence, 2),
            "predicted_7d_streams": self._predict_streams(score, track_data, 7),
            "predicted_14d_streams": self._predict_streams(score, track_data, 14),
            "predicted_28d_streams": self._predict_streams(score, track_data, 28),
            "factors": factors,
            "model_version": "rule_based_v1",  # Will be "ensemble_v1" when trained
        }

    def _extract_features(
        self,
        track_data: dict[str, Any],
        artist_data: dict[str, Any] | None,
    ) -> np.ndarray:
        """Extract ML features from track and artist data."""
        features = []

        # Track quality features
        features.append(track_data.get("tunescore", 50))
        features.append(track_data.get("hook_score", 50))
        features.append(track_data.get("production_quality", 50))

        # Sonic features
        sonic = track_data.get("sonic_genome", {})
        features.append(sonic.get("energy", 0.5))
        features.append(sonic.get("valence", 0.5))
        features.append(sonic.get("danceability", 0.5))
        features.append(sonic.get("tempo", 120) / 200)  # Normalize

        # Artist momentum (if available)
        if artist_data:
            features.append(artist_data.get("velocity_7d", 0) * 100)
            features.append(artist_data.get("velocity_28d", 0) * 100)
            features.append(artist_data.get("followers", 0) / 1000000)  # Normalize
        else:
            features.extend([0, 0, 0])

        # Playlist momentum
        features.append(track_data.get("playlist_adds_7d", 0))
        features.append(track_data.get("playlist_followers_total", 0) / 1000000)

        # Social signals
        features.append(track_data.get("social_mentions", 0))
        features.append(track_data.get("tiktok_videos", 0))

        return np.array(features).reshape(1, -1)

    def _rule_based_scoring(
        self,
        features: np.ndarray,
        track_data: dict[str, Any],
        artist_data: dict[str, Any] | None,
    ) -> tuple[float, float, dict[str, Any]]:
        """
        Rule-based breakout scoring (temporary until model is trained).

        Returns: (score, confidence, factors)
        """
        factors = {}
        score = 0

        # 1. Track Quality (0-30 points)
        tunescore = track_data.get("tunescore", 50)
        quality_score = (tunescore / 100) * 30
        score += quality_score
        factors["track_quality"] = round((tunescore / 100) * 100, 1)

        # 2. Artist Velocity (0-25 points)
        if artist_data:
            velocity_7d = artist_data.get("velocity_7d", 0)
            velocity_28d = artist_data.get("velocity_28d", 0)
            
            # Weight recent velocity more
            velocity_score = (velocity_7d * 0.6 + velocity_28d * 0.4) * 25
            velocity_score = max(0, min(25, velocity_score))  # Clamp
            score += velocity_score
            factors["artist_velocity"] = round(velocity_score / 25 * 100, 1)
        else:
            factors["artist_velocity"] = 50  # Neutral

        # 3. Playlist Momentum (0-20 points)
        playlist_adds = track_data.get("playlist_adds_7d", 0)
        playlist_score = min(20, playlist_adds * 2)  # 10 adds = max score
        score += playlist_score
        factors["playlist_momentum"] = round(playlist_score / 20 * 100, 1)

        # 4. Sonic Appeal (0-15 points)
        sonic = track_data.get("sonic_genome", {})
        energy = sonic.get("energy", 0.5)
        valence = sonic.get("valence", 0.5)
        danceability = sonic.get("danceability", 0.5)
        
        sonic_score = ((energy + valence + danceability) / 3) * 15
        score += sonic_score
        factors["sonic_appeal"] = round(sonic_score / 15 * 100, 1)

        # 5. Social Signals (0-10 points)
        social_mentions = track_data.get("social_mentions", 0)
        tiktok_videos = track_data.get("tiktok_videos", 0)
        
        social_score = min(10, (social_mentions / 100) + (tiktok_videos / 50))
        score += social_score
        factors["social_signals"] = round(social_score / 10 * 100, 1)

        # Calculate confidence based on data completeness
        confidence = 0.7  # Base confidence
        if artist_data:
            confidence += 0.15
        if playlist_adds > 0:
            confidence += 0.1
        if social_mentions > 0 or tiktok_videos > 0:
            confidence += 0.05

        return score, min(1.0, confidence), factors

    def _predict_streams(
        self, breakout_score: float, track_data: dict[str, Any], days: int
    ) -> int:
        """Predict stream count based on breakout score."""
        # Base estimation: higher score = more streams
        # This is a simple heuristic; real model would use regression
        
        current_monthly = track_data.get("monthly_streams", 0)
        if current_monthly == 0:
            # New track estimation
            base_streams = int(breakout_score * 1000)
        else:
            # Existing track: project growth
            daily_avg = current_monthly / 30
            growth_factor = 1 + (breakout_score / 100)
            base_streams = int(daily_avg * days * growth_factor)

        return base_streams

    def train_model(
        self,
        training_data: list[dict[str, Any]],
        labels: list[int],
    ) -> dict[str, Any]:
        """
        Train the breakout prediction model.

        Args:
            training_data: List of track/artist feature dictionaries
            labels: List of binary labels (1 = became hit, 0 = didn't)

        Returns:
            Training metrics
        """
        if not self.available:
            return {"error": "ML libraries not available"}

        try:
            # Extract features from training data
            X = np.array(
                [self._extract_features(d, d.get("artist_data")) for d in training_data]
            ).squeeze()
            y = np.array(labels)

            # Scale features
            X_scaled = self.scaler.fit_transform(X)

            # Train RandomForest
            self.rf_model.fit(X_scaled, y)
            rf_score = self.rf_model.score(X_scaled, y)

            # Train XGBoost
            self.xgb_model.fit(X_scaled, y)
            xgb_score = self.xgb_model.score(X_scaled, y)

            # Create ensemble model (average predictions)
            self.model = {
                "rf": self.rf_model,
                "xgb": self.xgb_model,
                "type": "ensemble",
            }

            # Save models
            os.makedirs(os.path.dirname(self.MODEL_PATH), exist_ok=True)
            joblib.dump(self.model, self.MODEL_PATH)
            joblib.dump(self.scaler, self.SCALER_PATH)

            logger.info(f"✅ Model trained - RF: {rf_score:.3f}, XGB: {xgb_score:.3f}")

            return {
                "success": True,
                "rf_accuracy": round(rf_score, 3),
                "xgb_accuracy": round(xgb_score, 3),
                "training_samples": len(training_data),
            }

        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return {"error": str(e)}

