# DemocratIA - Parliamentary text summarizer

import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import ANTHROPIC_API_KEY


class Summarizer:
    """Generate accessible summaries of parliamentary texts."""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def summarize(self, text: str, context: str = "", dossier_titre: str = "", theme: str = "") -> str:
        """Summarize a parliamentary text in 3-5 sentences accessible to citizens.

        Args:
            text: The parliamentary text to summarize.
            context: Optional context (e.g., deputy name, group).
            dossier_titre: Title of the legislative dossier.
            theme: Theme of the dossier or debate.

        Returns:
            A clear, accessible summary in French.
        """
        system_prompt = (
            "Tu es un expert en vulgarisation parlementaire pour le projet DemocratIA. "
            "Ton public est compose de citoyens francais qui ne sont pas specialistes "
            "du droit ou de la politique. "
            "Regles :\n"
            "- Resume en 3 a 5 phrases claires, sans jargon juridique\n"
            "- Explique les enjeux concrets pour les citoyens\n"
            "- Mentionne les positions principales si le texte est un debat\n"
            "- Utilise un ton neutre et factuel\n"
            "- Ne prends pas position, reste objectif"
        )

        user_prompt = ""
        if dossier_titre:
            user_prompt += f"Dossier legislatif : {dossier_titre}\n"
        if theme:
            user_prompt += f"Theme : {theme}\n"
        if context:
            user_prompt += f"Contexte : {context}\n"
        if user_prompt:
            user_prompt += "\n"

        user_prompt += (
            "Resume le texte parlementaire suivant de maniere accessible "
            "pour un citoyen non-specialiste :\n\n"
            f"{text}"
        )

        message = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        return message.content[0].text
