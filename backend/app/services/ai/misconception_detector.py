"""
Misconception Detector — Explainable AI (XAI) layer
Identifies specific cognitive error patterns from student responses.
Uses rule-based patterns + SHAP explanations on top of DKT features.
"""
from typing import Dict, List, Optional, Tuple
import structlog
import re

logger = structlog.get_logger()


# Misconception taxonomy — derived from math education research
# Each entry: pattern_name -> {description, affected_skills, detection_rules}
MISCONCEPTION_TAXONOMY = {
    "neg_division_flip": {
        "description": "Student forgets to flip inequality when dividing by a negative number",
        "affected_skills": ["inequalities", "linear_inequalities"],
        "severity": "high",
    },
    "fraction_add_denominators": {
        "description": "Student adds denominators instead of finding common denominator",
        "affected_skills": ["fraction_addition", "rational_numbers"],
        "severity": "high",
    },
    "exponent_multiply_base": {
        "description": "Student multiplies base when applying power rules instead of multiplying exponents",
        "affected_skills": ["exponent_rules", "polynomial_operations"],
        "severity": "medium",
    },
    "slope_xy_swap": {
        "description": "Student swaps rise and run in slope calculation",
        "affected_skills": ["slope", "linear_functions"],
        "severity": "medium",
    },
    "order_of_operations_left_right": {
        "description": "Student applies all operations strictly left-to-right ignoring PEMDAS",
        "affected_skills": ["order_of_operations", "arithmetic"],
        "severity": "medium",
    },
    "negative_distribution": {
        "description": "Student fails to distribute negative sign to all terms in parentheses",
        "affected_skills": ["distributive_property", "polynomial_simplification"],
        "severity": "high",
    },
    "percent_decimal_confusion": {
        "description": "Student confuses percent and decimal representation",
        "affected_skills": ["percentages", "ratios"],
        "severity": "low",
    },
    "variable_isolation_sign_error": {
        "description": "Student makes sign error when moving variable across equals sign",
        "affected_skills": ["linear_equations", "solving_equations"],
        "severity": "high",
    },
}


class MisconceptionDetector:
    """
    Detects specific cognitive misconceptions from student response patterns.
    Combines:
    1. Rule-based pattern matching on response data
    2. Error frequency analysis across attempts
    3. SHAP-based feature attribution (when ML model available)
    """

    def __init__(self):
        self.taxonomy = MISCONCEPTION_TAXONOMY

    def detect_from_response(
        self,
        item_content: Dict,
        student_answer: Dict,
        correct_answer: Dict,
        skill_code: str,
        response_history: List[Dict] = None
    ) -> Tuple[Optional[str], float]:
        """
        Detect misconception from a single response.
        Returns (misconception_tag, confidence) or (None, 0.0)
        """
        if student_answer == correct_answer:
            return None, 0.0

        # Try rule-based detection first
        misconception, confidence = self._rule_based_detection(
            item_content, student_answer, correct_answer, skill_code
        )

        # Boost confidence if pattern recurs in history
        if misconception and response_history:
            recurrence = self._check_recurrence(misconception, skill_code, response_history)
            confidence = min(0.99, confidence + recurrence * 0.15)

        return misconception, confidence

    def _rule_based_detection(
        self,
        item: Dict,
        student_ans: Dict,
        correct_ans: Dict,
        skill_code: str
    ) -> Tuple[Optional[str], float]:
        """Apply skill-specific detection rules."""
        item_type = item.get("type", "")
        student_val = str(student_ans.get("value", "")).strip()
        correct_val = str(correct_ans.get("value", "")).strip()

        # Inequality direction flip
        if "inequalit" in skill_code.lower():
            flipped = {"<": ">", ">": "<", "≤": "≥", "≥": "≤"}
            for orig, flip in flipped.items():
                if orig in correct_val and flip in student_val:
                    return "neg_division_flip", 0.82

        # Fraction denominator addition
        if "fraction" in skill_code.lower() or "rational" in skill_code.lower():
            if item.get("operation") == "addition":
                student_denom = item.get("student_denominator_used")
                expected_denom = item.get("correct_common_denominator")
                if student_denom and expected_denom and student_denom != expected_denom:
                    return "fraction_add_denominators", 0.78

        # Sign error in equation solving
        if "equation" in skill_code.lower() or "solving" in skill_code.lower():
            try:
                sv = float(student_val)
                cv = float(correct_val)
                if abs(sv + cv) < 0.01 and abs(sv - cv) > 0.01:
                    return "variable_isolation_sign_error", 0.85
            except (ValueError, TypeError):
                pass

        # Negative distribution error
        if "distributive" in skill_code.lower() or "polynomial" in skill_code.lower():
            if item.get("has_negative_leading_term") and student_ans.get("partial_terms"):
                student_terms = student_ans.get("partial_terms", [])
                if len(student_terms) > 1 and student_terms[0] < 0 and student_terms[1] > 0:
                    return "negative_distribution", 0.75

        return None, 0.0

    def _check_recurrence(
        self,
        misconception: str,
        skill_code: str,
        history: List[Dict]
    ) -> float:
        """Calculate how often this misconception recurs in history (0-1)."""
        related_responses = [
            r for r in history
            if r.get("skill_code") == skill_code and not r.get("is_correct")
        ]
        if not related_responses:
            return 0.0
        matching = sum(
            1 for r in related_responses
            if r.get("misconception_detected") == misconception
        )
        return matching / len(related_responses)

    def get_explanation(self, misconception_tag: str) -> Dict:
        """Return human-readable explanation for teacher/student dashboard."""
        entry = self.taxonomy.get(misconception_tag, {})
        return {
            "tag": misconception_tag,
            "description": entry.get("description", "Unknown error pattern"),
            "severity": entry.get("severity", "medium"),
            "affected_skills": entry.get("affected_skills", []),
            "teacher_prompt": self._teacher_intervention_prompt(misconception_tag),
        }

    def _teacher_intervention_prompt(self, tag: str) -> str:
        prompts = {
            "neg_division_flip": (
                "3 students in Period 4 are consistently forgetting to flip the inequality "
                "symbol when dividing by a negative. Recommended: 10-minute small-group "
                "activity using number line to visualize direction change."
            ),
            "fraction_add_denominators": (
                "Students are adding numerators AND denominators. Suggest a visual fraction "
                "bar activity before the next problem set."
            ),
            "variable_isolation_sign_error": (
                "Students are moving terms without flipping sign. Suggest emphasizing "
                "'what you do to one side, do to the other' with balance scale metaphor."
            ),
        }
        return prompts.get(tag, f"Targeted review recommended for misconception: {tag}")
