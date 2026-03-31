"""Sentiment analysis service using Claude API."""

import json

import anthropic
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import ANTHROPIC_API_KEY


class SentimentResult(BaseModel):
    label: str  # "favorable", "defavorable", "neutre"
    score: float  # 0.0 to 1.0
    explanation: str


class SentimentAnalyzer:
    """Analyze sentiment of parliamentary texts."""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def analyze(self, text: str, theme: str = "") -> dict:
        """Analyze the sentiment of a parliamentary text.

        Args:
            text: The text to analyze.
            theme: The theme or subject being discussed.

        Returns:
            Dict with label, score, and explanation.
        """
        system_prompt = (
            "Tu es un analyste politique objectif. Tu analyses le sentiment "
            "des textes parlementaires par rapport a un sujet donne."
        )

        user_prompt = (
            "Analyse le sentiment du texte suivant"
        )
        if theme:
            user_prompt += f" par rapport au theme \"{theme}\""
        user_prompt += ".\n\n"
        user_prompt += f"Texte :\n{text}\n\n"
        user_prompt += (
            "Reponds UNIQUEMENT avec un objet JSON valide au format suivant :\n"
            '{"label": "favorable|defavorable|neutre", "score": 0.0-1.0, '
            '"explanation": "explication courte en francais"}\n\n'
            "- label : favorable, defavorable ou neutre\n"
            "- score : degre de certitude entre 0.0 et 1.0\n"
            "- explanation : explication en une phrase"
        )

        message = self.client.messages.create(
            model=self.model,
            max_tokens=300,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        response_text = message.content[0].text.strip()

        # Extract JSON from response
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            # Try to find JSON in the response
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start >= 0 and end > start:
                result = json.loads(response_text[start:end])
            else:
                result = {
                    "label": "neutre",
                    "score": 0.5,
                    "explanation": "Analyse non disponible",
                }

        return SentimentResult(**result).model_dump()
