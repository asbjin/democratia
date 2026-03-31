"""Summarization service using Claude API."""

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
    async def summarize(self, text: str, context: str = "") -> str:
        """Summarize a parliamentary text in 3-5 sentences accessible to citizens.

        Args:
            text: The parliamentary text to summarize.
            context: Optional context (e.g., dossier title, theme).

        Returns:
            A clear, accessible summary in French.
        """
        system_prompt = (
            "Tu es un assistant specialise dans la vulgarisation de l'activite "
            "parlementaire francaise. Ton role est de rendre les textes legislatifs "
            "et les debats accessibles a tous les citoyens."
        )

        user_prompt = "Resume le texte parlementaire suivant en 3 a 5 phrases claires et accessibles.\n\n"
        if context:
            user_prompt += f"Contexte : {context}\n\n"
        user_prompt += f"Texte :\n{text}"

        message = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        return message.content[0].text
