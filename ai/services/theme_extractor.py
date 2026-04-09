"""Theme extraction service using LLM API."""

import json

import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import ANTHROPIC_API_KEY

# Predefined parliamentary themes for classification
PARLIAMENTARY_THEMES = [
    "Budget et finances publiques",
    "Social et retraites",
    "Immigration et asile",
    "Environnement et ecologie",
    "Numerique et donnees",
    "Sante publique",
    "Education et recherche",
    "Securite et defense",
    "Logement et urbanisme",
    "Emploi et travail",
    "Justice et droits",
    "Agriculture et alimentation",
    "Transports et mobilite",
    "Culture et patrimoine",
    "Affaires europeennes",
    "Outre-mer",
    "Collectivites territoriales",
]


class ThemeExtractor:
    """Extract and classify themes from parliamentary texts."""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def extract_themes(self, text: str, max_themes: int = 3) -> list[dict]:
        """Extract main themes from a parliamentary text.

        Args:
            text: The parliamentary text to analyze.
            max_themes: Maximum number of themes to return.

        Returns:
            List of dicts with 'theme', 'confidence', and 'keywords'.
        """
        themes_list = "\n".join(f"- {t}" for t in PARLIAMENTARY_THEMES)

        system_prompt = (
            "Tu es un classificateur de textes parlementaires. "
            "Tu identifies les themes principaux des debats et interventions "
            "de l'Assemblee Nationale francaise."
        )

        user_prompt = (
            f"Analyse le texte parlementaire suivant et identifie les {max_themes} "
            "themes principaux.\n\n"
            f"Themes de reference :\n{themes_list}\n\n"
            f"Texte :\n{text}\n\n"
            "Reponds UNIQUEMENT avec un tableau JSON valide au format suivant :\n"
            '[{"theme": "nom du theme", "confidence": 0.0-1.0, '
            '"keywords": ["mot1", "mot2", "mot3"]}]\n\n'
            "- theme : un des themes de reference ou un theme libre si aucun ne correspond\n"
            "- confidence : degre de certitude entre 0.0 et 1.0\n"
            "- keywords : 3 mots-cles du texte lies a ce theme"
        )

        message = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        response_text = message.content[0].text.strip()

        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            start = response_text.find("[")
            end = response_text.rfind("]") + 1
            if start >= 0 and end > start:
                result = json.loads(response_text[start:end])
            else:
                result = [{"theme": "Non classifie", "confidence": 0.0, "keywords": []}]

        return result[:max_themes]

    def classify(self, text: str) -> str:
        """Return the single most likely theme for a text.

        Args:
            text: The parliamentary text to classify.

        Returns:
            The name of the most likely theme.
        """
        themes = self.extract_themes(text, max_themes=1)
        if themes:
            return themes[0]["theme"]
        return "Non classifie"
