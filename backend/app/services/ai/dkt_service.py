"""
Deep Knowledge Tracing (DKT) Service
Estimates student mastery probability for each math skill
using LSTM-based sequence modeling of interaction history.
"""
import numpy as np
from typing import List, Dict, Tuple
import structlog

logger = structlog.get_logger()


class DKTService:
    """
    Deep Knowledge Tracing inference service.
    
    Architecture:
    - LSTM encoder processes sequence of (skill_id, correct) pairs
    - Output layer gives P(mastery) for each skill at each timestep
    - Trained on synthetic + real interaction data
    - Updated via RLHF feedback loop
    """

    def __init__(self, model_path: str = None, num_skills: int = 500):
        self.num_skills = num_skills
        self.model = None
        self.model_path = model_path
        self._load_model()

    def _load_model(self):
        """Load trained TensorFlow DKT model or initialize with defaults."""
        try:
            import tensorflow as tf
            if self.model_path:
                self.model = tf.keras.models.load_model(self.model_path)
                logger.info("DKT model loaded", path=self.model_path)
            else:
                self.model = self._build_default_model()
                logger.info("DKT default model initialized")
        except Exception as e:
            logger.warning("TensorFlow not available, using heuristic DKT", error=str(e))
            self.model = None

    def _build_default_model(self):
        """Build LSTM-based DKT architecture for development/demo."""
        try:
            import tensorflow as tf
            inputs = tf.keras.Input(shape=(None, self.num_skills * 2))
            x = tf.keras.layers.LSTM(200, return_sequences=True)(inputs)
            x = tf.keras.layers.Dropout(0.3)(x)
            x = tf.keras.layers.LSTM(100, return_sequences=True)(x)
            outputs = tf.keras.layers.Dense(self.num_skills, activation="sigmoid")(x)
            model = tf.keras.Model(inputs, outputs)
            model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
            return model
        except Exception:
            return None

    def encode_interactions(
        self, interactions: List[Dict]
    ) -> np.ndarray:
        """
        Encode interaction history as one-hot skill vectors.
        Each interaction: {skill_index: int, correct: 0|1}
        Returns shape: (1, seq_len, num_skills * 2)
        """
        seq_len = len(interactions)
        encoded = np.zeros((1, seq_len, self.num_skills * 2), dtype=np.float32)
        for t, interaction in enumerate(interactions):
            skill_idx = interaction.get("skill_index", 0) % self.num_skills
            correct   = interaction.get("correct", 0)
            offset    = skill_idx + (self.num_skills if correct else 0)
            encoded[0, t, offset] = 1.0
        return encoded

    def predict_mastery(
        self,
        interactions: List[Dict],
        target_skill_indices: List[int]
    ) -> Dict[int, float]:
        """
        Predict current mastery probability for each target skill
        given the student's interaction history.

        Returns: {skill_index: mastery_probability}
        """
        if not interactions:
            return {idx: 0.1 for idx in target_skill_indices}

        if self.model is not None:
            try:
                encoded = self.encode_interactions(interactions)
                predictions = self.model.predict(encoded, verbose=0)
                last_step = predictions[0, -1, :]
                return {
                    idx: float(np.clip(last_step[idx % self.num_skills], 0.0, 1.0))
                    for idx in target_skill_indices
                }
            except Exception as e:
                logger.warning("DKT inference failed, using heuristic", error=str(e))

        # Heuristic fallback: Bayesian-style moving average
        return self._heuristic_mastery(interactions, target_skill_indices)

    def _heuristic_mastery(
        self,
        interactions: List[Dict],
        target_skill_indices: List[int]
    ) -> Dict[int, float]:
        """
        Fallback mastery estimation using exponential moving average.
        Used when TF model unavailable (MVP / demo mode).
        """
        skill_data: Dict[int, List[float]] = {}
        for interaction in interactions:
            idx     = interaction.get("skill_index", 0) % self.num_skills
            correct = float(interaction.get("correct", 0))
            skill_data.setdefault(idx, []).append(correct)

        results = {}
        for idx in target_skill_indices:
            history = skill_data.get(idx, [])
            if not history:
                results[idx] = 0.15
            else:
                # Exponential moving average — recent attempts weighted more
                alpha  = 0.3
                mastery = history[0]
                for val in history[1:]:
                    mastery = alpha * val + (1 - alpha) * mastery
                # Sigmoid-style clamp
                results[idx] = float(np.clip(mastery + 0.1 * len(history) / (len(history) + 5), 0.05, 0.97))
        return results

    def update_after_response(
        self,
        current_mastery: float,
        is_correct: bool,
        skill_difficulty: float = 0.5
    ) -> Tuple[float, float]:
        """
        Compute updated mastery after a single response.
        Returns (new_mastery, mastery_delta).
        Used for real-time dashboard updates without full re-inference.
        """
        learn_rate = 0.15 if is_correct else -0.08
        difficulty_adj = (1 - skill_difficulty) * 0.1
        delta = learn_rate + (difficulty_adj if is_correct else 0)
        new_mastery = float(np.clip(current_mastery + delta, 0.0, 1.0))
        return new_mastery, new_mastery - current_mastery
