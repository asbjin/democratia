# DemocratIA - Deputy photo downloader

import logging
import os
from pathlib import Path

import requests
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import declarative_base, sessionmaker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

Base = declarative_base()

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://democratia:democratia_secret@localhost:5432/democratia",
)

PHOTO_URL_PATTERN = "https://www.assemblee-nationale.fr/dyn/deputes/{uid}/photo"
PHOTOS_DIR = Path(__file__).parent.parent.parent / "frontend" / "public" / "photos"


class Depute(Base):
    __tablename__ = "deputes"
    id = Column(String, primary_key=True)
    photo_url = Column(String)


def ensure_photos_dir():
    """Create photos directory if it doesn't exist."""
    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)


def download_photo(uid: str) -> str | None:
    """Download a deputy's photo. Returns local path or None on failure."""
    photo_path = PHOTOS_DIR / f"{uid}.jpg"

    if photo_path.exists():
        return f"/photos/{uid}.jpg"

    url = PHOTO_URL_PATTERN.format(uid=uid)

    try:
        response = requests.get(url, timeout=15, stream=True)
        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            if "image" in content_type:
                with open(photo_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=4096):
                        f.write(chunk)
                return f"/photos/{uid}.jpg"
        logger.debug(f"Photo not found for {uid} (HTTP {response.status_code})")
    except requests.RequestException as e:
        logger.debug(f"Failed to download photo for {uid}: {e}")

    return None


def import_photos():
    """Download photos for all deputies and update photo_url."""
    ensure_photos_dir()

    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        deputes = session.query(Depute).all()
        total = len(deputes)
        downloaded = 0
        skipped = 0

        logger.info(f"Processing {total} deputies for photo download")

        for i, depute in enumerate(deputes, 1):
            if depute.photo_url and (PHOTOS_DIR / f"{depute.id}.jpg").exists():
                skipped += 1
                continue

            local_path = download_photo(depute.id)
            if local_path:
                depute.photo_url = local_path
                downloaded += 1

            if i % 50 == 0:
                session.commit()
                logger.info(f"  Progress: {i}/{total} ({downloaded} downloaded, {skipped} skipped)")

        session.commit()
        logger.info(f"Photo import complete: {downloaded} downloaded, {skipped} skipped, {total - downloaded - skipped} not found")

    except Exception as e:
        session.rollback()
        logger.error(f"Photo import failed: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    import_photos()
