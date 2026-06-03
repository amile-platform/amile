"""
AI Intervention Generator
Generates culturally-contextualized, standards-aligned project-based
learning modules using fine-tuned LLM + template fallback.
"""
from typing import Dict, List, Optional
import structlog
import json

logger = structlog.get_logger()


# Project-based learning context themes mapped to real-world domains
PBL_THEMES = {
    "urban":        ["transit scheduling", "urban garden design", "community budget allocation", "building codes"],
    "rural":        ["farm yield optimization", "water table measurement", "crop pricing", "weather patterns"],
    "sports":       ["basketball statistics", "track and field timing", "game strategy optimization"],
    "music":        ["beat fractions", "frequency ratios", "concert revenue modeling"],
    "technology":   ["app pricing models", "social media growth rates", "coding salary comparisons"],
    "environmental":["carbon footprint calculations", "solar panel efficiency", "water conservation"],
    "healthcare":   ["medication dosing", "hospital resource allocation", "nutrition data analysis"],
}


SYSTEM_PROMPT = """You are an expert mathematics curriculum designer specializing in 
project-based learning for high school students in underserved communities.
Generate a complete project-based learning module that:
1. Uses a real-world context relevant to the student's cultural background
2. Directly targets the specified misconception
3. Aligns to the specified Common Core or TEKS standard
4. Includes scaffolded steps appropriate for the student's reading level
5. Embeds mathematical reasoning without making it feel like a test
Return JSON only."""


class InterventionGenerator:
    """
    Generates personalized intervention modules.
    Primary: LLM-based generation (LLaMA-3-8B fine-tuned)
    Fallback: Template-based generation from skill taxonomy
    """

    def __init__(self, llm_client=None):
        self.llm = llm_client
        self.templates = self._load_templates()

    def generate(
        self,
        skill_code: str,
        skill_name: str,
        misconception_tag: Optional[str],
        student_profile: Dict,
        grade_level: int,
    ) -> Dict:
        """
        Generate a complete intervention module.
        Returns structured module dict ready for frontend rendering.
        """
        context_theme = self._select_theme(student_profile)
        reading_level = student_profile.get("reading_level_grade", grade_level)
        language      = student_profile.get("primary_language", "English")

        if self.llm:
            try:
                return self._llm_generate(
                    skill_code, skill_name, misconception_tag,
                    context_theme, reading_level, language, grade_level
                )
            except Exception as e:
                logger.warning("LLM generation failed, using template", error=str(e))

        return self._template_generate(
            skill_code, skill_name, misconception_tag,
            context_theme, reading_level, language, grade_level
        )

    def _llm_generate(
        self, skill_code, skill_name, misconception_tag,
        theme, reading_level, language, grade_level
    ) -> Dict:
        """Call fine-tuned LLM to generate module."""
        prompt = f"""Generate a project-based learning module:
- Skill: {skill_name} ({skill_code})
- Grade: {grade_level}
- Misconception to address: {misconception_tag or 'general reinforcement'}
- Context theme: {theme}
- Student reading level: Grade {reading_level:.1f}
- Language: {language}

Return JSON with keys:
title, context_story, learning_objectives (list),
steps (list of {{step_number, instruction, math_prompt, hint}}),
reflection_questions (list), standards_alignment (list)"""

        response = self.llm.complete(SYSTEM_PROMPT, prompt)
        return json.loads(response)

    def _template_generate(
        self, skill_code, skill_name, misconception_tag,
        theme, reading_level, language, grade_level
    ) -> Dict:
        """Template-based fallback generator."""
        theme_examples = PBL_THEMES.get(theme, PBL_THEMES["urban"])
        context = theme_examples[hash(skill_code) % len(theme_examples)]

        title = f"{skill_name}: {context.title()} Challenge"
        
        steps = [
            {
                "step_number": 1,
                "instruction": f"Explore the real-world scenario: {context}.",
                "math_prompt": f"Identify where {skill_name} appears in this scenario.",
                "hint": "Look for quantities that change or relate to each other.",
            },
            {
                "step_number": 2,
                "instruction": "Set up the mathematical model.",
                "math_prompt": f"Write an expression or equation using {skill_name}.",
                "hint": "Start by defining your variables.",
            },
            {
                "step_number": 3,
                "instruction": "Solve and verify your answer.",
                "math_prompt": "Check your solution by substituting back.",
                "hint": self._misconception_hint(misconception_tag),
            },
            {
                "step_number": 4,
                "instruction": "Present your solution.",
                "math_prompt": "Explain your reasoning in 2-3 sentences.",
                "hint": "Imagine explaining this to a classmate who missed class.",
            },
        ]

        return {
            "title": title,
            "skill_code": skill_code,
            "grade_level": grade_level,
            "context_story": (
                f"You are working on a {context} project for your community. "
                f"To complete it, you need to apply your knowledge of {skill_name}."
            ),
            "learning_objectives": [
                f"Apply {skill_name} in a real-world context",
                "Identify and correct common errors",
                "Communicate mathematical reasoning clearly",
            ],
            "steps": steps,
            "reflection_questions": [
                f"Where else in daily life might you use {skill_name}?",
                "What was the trickiest part of this problem? Why?",
                "How would you explain this skill to a friend?",
            ],
            "standards_alignment": [skill_code],
            "language": language,
            "estimated_minutes": 20 + (grade_level - 6) * 3,
            "generated_by": "template",
        }

    def _select_theme(self, student_profile: Dict) -> str:
        """Select culturally relevant theme from student profile."""
        prefs = student_profile.get("learning_preferences", {})
        preferred_theme = prefs.get("context_theme")
        if preferred_theme and preferred_theme in PBL_THEMES:
            return preferred_theme
        # Default: urban (most broadly applicable for underserved HS)
        return "urban"

    def _misconception_hint(self, tag: Optional[str]) -> str:
        hints = {
            "neg_division_flip":           "Remember: dividing by a negative number flips the inequality direction!",
            "fraction_add_denominators":   "Never add the denominators — find a common denominator first.",
            "variable_isolation_sign_error":"When moving a term to the other side, always change its sign.",
            "negative_distribution":        "The negative sign must be distributed to EVERY term inside the parentheses.",
        }
        return hints.get(tag, "Check your work by substituting your answer back into the original problem.")

    def _load_templates(self) -> Dict:
        return {}
