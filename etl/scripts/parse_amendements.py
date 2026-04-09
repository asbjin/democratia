# DemocratIA - Parse amendements from AN open data

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def parse_amendement(data: dict) -> dict | None:
    """Parse a single amendement JSON into a flat dict."""
    try:
        amendement = data.get("amendement", data)

        uid = amendement.get("uid", "")
        if not uid:
            return None

        # Auteur
        signataires = amendement.get("signataires", {})
        auteur = signataires.get("auteur", {})
        depute_id = auteur.get("acteurRef", "")

        # Contenu
        corps = amendement.get("corps", {})
        contenu = corps.get("contenuAuteur", {})
        texte = contenu.get("dispositif", "")
        objet = contenu.get("exposeSommaire", "")

        # Metadata
        date_depot = amendement.get("dateDepot", "")
        sort = amendement.get("sort", {})
        if isinstance(sort, dict):
            sort = sort.get("sortEnSeance", sort.get("code", ""))

        dossier_id = amendement.get("dossierRef", "")

        return {
            "id": uid,
            "depute_id": depute_id,
            "dossier_id": dossier_id,
            "texte": texte,
            "sort": sort if isinstance(sort, str) else "",
            "date": date_depot,
            "objet": objet,
        }
    except (KeyError, TypeError) as e:
        logger.warning(f"Failed to parse amendement: {e}")
        return None


def parse_all_amendements(extract_dir: Path) -> list[dict]:
    """Parse all amendement JSON files from the extracted directory."""
    amendements = []
    json_files = list(extract_dir.rglob("*.json"))
    logger.info(f"Found {len(json_files)} JSON files in {extract_dir}")

    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            result = parse_amendement(data)
            if result and result["depute_id"]:
                amendements.append(result)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to read {json_file}: {e}")

    logger.info(f"Parsed {len(amendements)} amendements")
    return amendements


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) > 1:
        result = parse_all_amendements(Path(sys.argv[1]))
        print(f"Parsed {len(result)} amendements")
