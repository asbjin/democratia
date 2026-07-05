# DemocratIA - Parse acteurs JSON from AN open data

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def find_json_files(extract_dir: Path) -> list[Path]:
    """Recursively find all JSON files in the extracted directory."""
    return list(extract_dir.rglob("*.json"))


def parse_acteur(data: dict) -> dict | None:
    """Parse a single acteur JSON into a flat dict."""
    try:
        acteur = data.get("acteur", data)

        uid = acteur["uid"]["#text"] if isinstance(acteur["uid"], dict) else acteur["uid"]

        etat_civil = acteur.get("etatCivil", {})
        ident = etat_civil.get("ident", {})
        nom = ident.get("nom", "")
        prenom = ident.get("prenom", "")
        date_naissance = etat_civil.get("infoNaissance", {}).get("dateNais", "")
        sexe = ident.get("civ", "")

        # Get current political group
        groupe_politique = ""
        mandats = acteur.get("mandats", {}).get("mandat", [])
        if isinstance(mandats, dict):
            mandats = [mandats]

        for mandat in mandats:
            if mandat.get("typeOrgane") == "GP":
                infos = mandat.get("infosQualite", {}).get("codeQualite", "")
                organe_ref = mandat.get("organes", {}).get("organeRef", "")
                if not mandat.get("dateFin"):
                    groupe_politique = organe_ref
                    break

        # Get circonscription
        circonscription = ""
        departement = ""
        for mandat in mandats:
            if mandat.get("typeOrgane") == "ASSEMBLEE":
                election = mandat.get("election", {})
                lieu = election.get("lieu", {})
                departement = lieu.get("departement", "")
                circo = lieu.get("numCirco", "")
                if departement and circo:
                    circonscription = f"{departement} - {circo}"
                break

        return {
            "uid": uid,
            "nom": nom,
            "prenom": prenom,
            "dateNaissance": date_naissance,
            "sexe": sexe,
            "groupe_politique": groupe_politique,
            "circonscription": circonscription,
            "departement": departement,
        }
    except (KeyError, TypeError) as e:
        logger.warning(f"Failed to parse acteur: {e}")
        return None


def parse_groupe(data: dict) -> dict | None:
    """Parse a GP (groupe politique) organe JSON into a flat dict."""
    organe = data.get("organe", data)
    if organe.get("codeType") != "GP":
        return None

    uid = organe.get("uid")
    uid = uid["#text"] if isinstance(uid, dict) else uid
    if not uid:
        return None

    couleur = organe.get("couleurAssociee")
    if not isinstance(couleur, str):
        couleur = ""

    return {
        "id": uid,
        "nom": organe.get("libelle", "") or "",
        "sigle": organe.get("libelleAbrege", "") or "",
        "couleur": couleur,
    }


def parse_all_groupes(extract_dir: Path) -> list[dict]:
    """Parse all GP organes into groupe dicts, deduplicated by id."""
    groupes = {}
    for json_file in find_json_files(extract_dir):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            continue
        result = parse_groupe(data)
        if result:
            groupes[result["id"]] = result

    logger.info(f"Parsed {len(groupes)} groupes politiques")
    return list(groupes.values())


def parse_all_acteurs(extract_dir: Path) -> list[dict]:
    """Parse all acteur JSON files from the extracted directory."""
    acteurs = []
    json_files = find_json_files(extract_dir)
    logger.info(f"Found {len(json_files)} JSON files in {extract_dir}")

    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            result = parse_acteur(data)
            if result:
                acteurs.append(result)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to read {json_file}: {e}")

    logger.info(f"Parsed {len(acteurs)} acteurs")
    return acteurs


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) > 1:
        result = parse_all_acteurs(Path(sys.argv[1]))
        print(f"Parsed {len(result)} acteurs")
