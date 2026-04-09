# DemocratIA - Parse scrutins JSON from AN open data

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def parse_vote(vote_data: dict, scrutin_id: str) -> list[dict]:
    """Parse votes from a vote group."""
    votes = []

    for position in ["pours", "contres", "abstentions"]:
        position_label = position.rstrip("s")
        if position_label == "pour":
            pos = "pour"
        elif position_label == "contre":
            pos = "contre"
        else:
            pos = "abstention"

        group_data = vote_data.get(position, {})
        votants = group_data.get("votant", [])
        if isinstance(votants, dict):
            votants = [votants]

        for votant in votants:
            acteur_ref = votant.get("acteurRef", "")
            if acteur_ref:
                votes.append({
                    "scrutin_id": scrutin_id,
                    "depute_id": acteur_ref,
                    "position": pos,
                })

    return votes


def parse_scrutin(data: dict) -> tuple[dict, list[dict]]:
    """Parse a single scrutin JSON. Returns (scrutin_dict, list_of_votes)."""
    scrutin = data.get("scrutin", data)

    uid = scrutin.get("uid", "")
    titre = scrutin.get("titre", "")
    date = scrutin.get("dateScrutin", "")
    sort = scrutin.get("sort", {}).get("code", "")

    synthese = scrutin.get("syntheseVote", {})
    decompte = synthese.get("decompte", {})
    nb_pour = int(decompte.get("pour", 0))
    nb_contre = int(decompte.get("contre", 0))
    nb_abstention = int(decompte.get("abstentions", 0))

    dossier_ref = scrutin.get("dossierRef", None)

    scrutin_dict = {
        "id": uid,
        "titre": titre,
        "date": date,
        "nb_pour": nb_pour,
        "nb_contre": nb_contre,
        "nb_abstention": nb_abstention,
        "dossier_id": dossier_ref,
    }

    # Parse individual votes
    all_votes = []
    ventilation = scrutin.get("ventilationVotes", {}).get("organe", {})
    groupes = ventilation.get("groupes", {}).get("groupe", [])
    if isinstance(groupes, dict):
        groupes = [groupes]

    for groupe in groupes:
        vote_data = groupe.get("vote", {}).get("decompteNominatif", {})
        if vote_data:
            all_votes.extend(parse_vote(vote_data, uid))

    return scrutin_dict, all_votes


def parse_all_scrutins(extract_dir: Path) -> tuple[list[dict], list[dict]]:
    """Parse all scrutin JSON files. Returns (scrutins, votes)."""
    scrutins = []
    all_votes = []
    json_files = list(extract_dir.rglob("*.json"))
    logger.info(f"Found {len(json_files)} JSON files in {extract_dir}")

    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            scrutin_dict, votes = parse_scrutin(data)
            scrutins.append(scrutin_dict)
            all_votes.extend(votes)
        except (json.JSONDecodeError, IOError, KeyError) as e:
            logger.warning(f"Failed to parse {json_file}: {e}")

    logger.info(f"Parsed {len(scrutins)} scrutins with {len(all_votes)} votes")
    return scrutins, all_votes


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) > 1:
        scrutins, votes = parse_all_scrutins(Path(sys.argv[1]))
        print(f"Parsed {len(scrutins)} scrutins, {len(votes)} votes")
