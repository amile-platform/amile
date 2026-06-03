"""
Bayesian Knowledge Tracing (BKT) Service
Classic 4-parameter HMM model for per-skill mastery estimation.
Used alongside DKT — ensemble of both gives higher accuracy.
"""
from typing import Dict, List, Tuple
import math
import structlog

logger = structlog.get_logger()


# Default BKT parameters per skill difficulty tier
DEFAULT_PARAMS = {
    "easy":   {"p_learn": 0.35, "p_guess": 0.25, "p_slip": 0.10, "p_init": 0.30},
    "medium": {"p_learn": 0.25, "p_guess": 0.20, "p_slip": 0.15, "p_init": 0.15},
    "hard":   {"p_learn": 0.15, "p_guess": 0.15, "p_slip": 0.20, "p_init": 0.05},
}


class BKTService:
    """
    Bayesian Knowledge Tracing implementation.

    State: P(mastered) — probability student has mastered the skill.
    Updated using Bayes rule after each correct/incorrect response.
    """

    def __init__(self):
        self.skill_params: Dict[str, dict] = {}

    def get_params(self, skill_code: str, difficulty: float = 0.5) -> dict:
        """Return BKT parameters for a skill, using difficulty tier as default."""
        if skill_code in self.skill_params:
            return self.skill_params[skill_code]
        tier = "easy" if difficulty < 0.35 else ("hard" if difficulty > 0.65 else "medium")
        return DEFAULT_PARAMS[tier]

    def update(
        self,
        p_mastered: float,
        is_correct: bool,
        skill_code: str,
        difficulty: float = 0.5
    ) -> Tuple[float, dict]:
        """
        Apply one BKT update step.

        Args:
            p_mastered: prior P(mastered)
            is_correct: whether response was correct
            skill_code: skill identifier for parameter lookup
            difficulty: skill difficulty [0,1]

        Returns:
            (updated_p_mastered, debug_info)
        """
        params    = self.get_params(skill_code, difficulty)
        p_learn   = params["p_learn"]
        p_guess   = params["p_guess"]
        p_slip    = params["p_slip"]

        # P(correct | mastered) and P(correct | not mastered)
        p_correct_given_mastered     = 1 - p_slip
        p_correct_given_not_mastered = p_guess

        if is_correct:
            p_evidence_mastered     = p_correct_given_mastered
            p_evidence_not_mastered = p_correct_given_not_mastered
        else:
            p_evidence_mastered     = p_slip
            p_evidence_not_mastered = 1 - p_guess

        # Bayes update
        numerator   = p_evidence_mastered * p_mastered
        denominator = (numerator + p_evidence_not_mastered * (1 - p_mastered))
        p_mastered_given_evidence = numerator / denominator if denominator > 0 else p_mastered

        # Learning opportunity: P(mastered after) = P(mastered after obs) + P(learn | not mastered after obs)
        p_not_mastered = 1 - p_mastered_given_evidence
        p_mastered_new = p_mastered_given_evidence + p_not_mastered * p_learn
        p_mastered_new = max(0.01, min(0.99, p_mastered_new))

        debug = {
            "prior": p_mastered,
            "posterior_before_learning": p_mastered_given_evidence,
            "posterior_after_learning":  p_mastered_new,
            "params": params,
        }
        return p_mastered_new, debug

    def full_history_mastery(
        self,
        interactions: List[Dict],
        skill_code: str,
        difficulty: float = 0.5
    ) -> float:
        """
        Compute mastery from full interaction history for a single skill.
        interactions: list of {correct: bool}
        """
        params    = self.get_params(skill_code, difficulty)
        p_mastered = params["p_init"]
        for interaction in interactions:
            p_mastered, _ = self.update(
                p_mastered, interaction.get("correct", False), skill_code, difficulty
            )
        return p_mastered

    def predict_future_mastery(
        self,
        current_mastery: float,
        skill_code: str,
        future_attempts: int = 5,
        expected_accuracy: float = 0.7
    ) -> List[float]:
        """
        Project future mastery over N attempts assuming given accuracy rate.
        Used for 7-day and 30-day mastery predictions on equity dashboard.
        """
        trajectory = [current_mastery]
        p = current_mastery
        for _ in range(future_attempts):
            # Simulate a mix of correct and incorrect at expected_accuracy
            p_correct, _ = self.update(p, True,  skill_code)
            p_wrong, _   = self.update(p, False, skill_code)
            p = expected_accuracy * p_correct + (1 - expected_accuracy) * p_wrong
            trajectory.append(p)
        return trajectory
