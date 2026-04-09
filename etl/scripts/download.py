"""Download ZIP files from Assemblee Nationale Open Data."""

import logging
import os
import zipfile
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://data.assemblee-nationale.fr/static/openData/repository"
LEGISLATURE = "17"

DATASETS = {
    "acteurs": f"{BASE_URL}/AMO/tous_acteurs_mandats_organes_xi_legislature/AMO30_tous_acteurs_tous_mandats_tous_organes_historique.json.zip",
    "scrutins": f"{BASE_URL}/LOI/scrutins/Scrutins_XVII.json.zip",
    "comptes_rendus": f"{BASE_URL}/CR/seance/comptes-rendus-seance-XVII.json.zip",
}

DATA_DIR = Path(__file__).parent.parent / "data"


def ensure_data_dir():
    """Create data directory if it doesn't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def download_file(name: str, url: str) -> Path:
    """Download a ZIP file and return its path."""
    zip_path = DATA_DIR / f"{name}.zip"

    if zip_path.exists():
        logger.info(f"[{name}] ZIP already exists: {zip_path}")
        return zip_path

    logger.info(f"[{name}] Downloading from {url}...")
    response = requests.get(url, stream=True, timeout=120)
    response.raise_for_status()

    with open(zip_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    logger.info(f"[{name}] Downloaded: {zip_path} ({zip_path.stat().st_size} bytes)")
    return zip_path


def extract_zip(name: str, zip_path: Path) -> Path:
    """Extract a ZIP file and return the extraction directory."""
    extract_dir = DATA_DIR / name

    if extract_dir.exists():
        logger.info(f"[{name}] Already extracted: {extract_dir}")
        return extract_dir

    logger.info(f"[{name}] Extracting {zip_path}...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_dir)

    logger.info(f"[{name}] Extracted to {extract_dir}")
    return extract_dir


def download_all() -> dict[str, Path]:
    """Download and extract all datasets. Returns dict of name -> extracted dir."""
    ensure_data_dir()
    results = {}

    for name, url in DATASETS.items():
        try:
            zip_path = download_file(name, url)
            extract_dir = extract_zip(name, zip_path)
            results[name] = extract_dir
        except requests.RequestException as e:
            logger.error(f"[{name}] Download failed: {e}")
        except zipfile.BadZipFile as e:
            logger.error(f"[{name}] Bad ZIP file: {e}")

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    download_all()
