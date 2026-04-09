# DemocratIA - Parse questions from AN open data

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def parse_question(data: dict) -> dict | None:
    """Parse a single question JSON into a flat dict."""
    try:
        question = data.get("question", data)

        uid = question.get("uid", "")
        if not uid:
            return None

        # Auteur
        auteur = question.get("auteur", {})
        depute_id = auteur.get("acteurRef", "")

        # Contenu
        texte_question = question.get("texteQuestion", "")
        texte_reponse = question.get("texteReponse", "")
        if isinstance(texte_reponse, dict):
            texte_reponse = texte_reponse.get("texte", "")

        # Metadata
        date_depot = question.get("dateDepot", "")
        theme = question.get("indexationAN", {}).get("rubrique", "")
        ministere = question.get("minAttrib", {}).get("libelle", "")

        if isinstance(ministere, dict):
            ministere = ministere.get("#text", "")

        return {
            "id": uid,
            "depute_id": depute_id,
            "date": date_depot,
            "theme": theme,
            "texte": texte_question,
            "reponse": texte_reponse,
            "ministere": ministere,
        }
    except (KeyError, TypeError) as e:
        logger.warning(f"Failed to parse question: {e}")
        return None


def parse_all_questions(extract_dir: Path) -> list[dict]:
    """Parse all question JSON files from the extracted directory."""
    questions = []
    json_files = list(extract_dir.rglob("*.json"))
    logger.info(f"Found {len(json_files)} JSON files in {extract_dir}")

    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            result = parse_question(data)
            if result and result["depute_id"]:
                questions.append(result)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to read {json_file}: {e}")

    logger.info(f"Parsed {len(questions)} questions")
    return questions


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) > 1:
        result = parse_all_questions(Path(sys.argv[1]))
        print(f"Parsed {len(result)} questions")
