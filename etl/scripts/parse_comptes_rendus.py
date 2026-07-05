# DemocratIA - Parse comptes-rendus de seance (syceron XML) into interventions

import logging
import re
import xml.etree.ElementTree as ET
from pathlib import Path

logger = logging.getLogger(__name__)


def _local(tag: str) -> str:
    """Strip XML namespace from a tag name."""
    return tag.split("}")[-1]


def _seance_date(root) -> str | None:
    """Return the seance date as YYYY-MM-DD from the dateSeance field."""
    for el in root.iter():
        if _local(el.tag) == "dateSeance" and el.text and len(el.text) >= 8:
            s = el.text
            return f"{s[0:4]}-{s[4:6]}-{s[6:8]}"
    return None


def parse_compte_rendu(path: Path) -> list[dict]:
    """Parse one seance XML file into a list of intervention dicts."""
    interventions = []
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as e:
        logger.warning(f"Bad XML {path}: {e}")
        return interventions

    date = _seance_date(root)

    for para in root.iter():
        if _local(para.tag) != "paragraphe":
            continue

        orateur_id = None
        texte = None
        for child in para:
            tag = _local(child.tag)
            if tag == "orateurs":
                for sub in child.iter():
                    if _local(sub.tag) == "id" and sub.text and sub.text.strip():
                        orateur_id = sub.text.strip()
                        break
            elif tag == "texte":
                texte = "".join(child.itertext())

        if not orateur_id or not orateur_id.isdigit() or not texte:
            continue

        texte = re.sub(r"\s+", " ", texte).strip()
        if not texte:
            continue

        interventions.append({
            "depute_id": f"PA{orateur_id}",
            "date": date,
            "texte": texte,
            "type_seance": "seance publique",
        })

    return interventions


def parse_all_comptes_rendus(extract_dir: Path) -> list[dict]:
    """Parse all seance XML files into intervention dicts."""
    interventions = []
    files = list(extract_dir.rglob("*.xml"))
    logger.info(f"Found {len(files)} compte-rendu XML files in {extract_dir}")

    for xml_file in files:
        interventions.extend(parse_compte_rendu(xml_file))

    logger.info(f"Parsed {len(interventions)} interventions")
    return interventions


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) > 1:
        result = parse_all_comptes_rendus(Path(sys.argv[1]))
        print(f"Parsed {len(result)} interventions")
