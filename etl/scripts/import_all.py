"""Orchestrator: download, parse, and import AN open data into PostgreSQL."""

import logging
import os
import sys

from sqlalchemy import create_engine, Column, String, Integer, Date, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

from download import download_all
from parse_acteurs import parse_all_acteurs
from parse_scrutins import parse_all_scrutins

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


class Depute(Base):
    __tablename__ = "deputes"

    id = Column(String, primary_key=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    date_naissance = Column(String)
    sexe = Column(String)
    groupe_politique_id = Column(String)
    circonscription = Column(String)
    departement = Column(String)


class Scrutin(Base):
    __tablename__ = "scrutins"

    id = Column(String, primary_key=True)
    titre = Column(Text)
    date = Column(String)
    nb_pour = Column(Integer, default=0)
    nb_contre = Column(Integer, default=0)
    nb_abstention = Column(Integer, default=0)
    dossier_id = Column(String, nullable=True)


class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scrutin_id = Column(String, ForeignKey("scrutins.id"), nullable=False)
    depute_id = Column(String, ForeignKey("deputes.id"), nullable=False)
    position = Column(String, nullable=False)


def import_deputes(session, acteurs: list[dict]):
    """Insert or update deputes."""
    count = 0
    for acteur in acteurs:
        depute = session.get(Depute, acteur["uid"])
        if depute is None:
            depute = Depute(
                id=acteur["uid"],
                nom=acteur["nom"],
                prenom=acteur["prenom"],
                date_naissance=acteur.get("dateNaissance", ""),
                sexe=acteur.get("sexe", ""),
                groupe_politique_id=acteur.get("groupe_politique", ""),
                circonscription=acteur.get("circonscription", ""),
                departement=acteur.get("departement", ""),
            )
            session.add(depute)
            count += 1

    session.commit()
    logger.info(f"Imported {count} new deputes")


def import_scrutins(session, scrutins: list[dict], votes: list[dict]):
    """Insert or update scrutins and votes."""
    scrutin_count = 0
    for s in scrutins:
        existing = session.get(Scrutin, s["id"])
        if existing is None:
            scrutin = Scrutin(
                id=s["id"],
                titre=s["titre"],
                date=s["date"],
                nb_pour=s["nb_pour"],
                nb_contre=s["nb_contre"],
                nb_abstention=s["nb_abstention"],
                dossier_id=s.get("dossier_id"),
            )
            session.add(scrutin)
            scrutin_count += 1

    session.commit()
    logger.info(f"Imported {scrutin_count} new scrutins")

    # Import votes (only for deputes that exist)
    existing_depute_ids = {d.id for d in session.query(Depute.id).all()}
    vote_count = 0
    for v in votes:
        if v["depute_id"] in existing_depute_ids:
            vote = Vote(
                scrutin_id=v["scrutin_id"],
                depute_id=v["depute_id"],
                position=v["position"],
            )
            session.add(vote)
            vote_count += 1

            if vote_count % 5000 == 0:
                session.commit()
                logger.info(f"  ... {vote_count} votes imported so far")

    session.commit()
    logger.info(f"Imported {vote_count} votes")


def main():
    logger.info("=== DemocratIA ETL Pipeline ===")

    # Step 1: Download
    logger.info("Step 1: Downloading datasets...")
    datasets = download_all()

    if not datasets:
        logger.error("No datasets downloaded. Exiting.")
        sys.exit(1)

    # Step 2: Parse
    logger.info("Step 2: Parsing data...")
    acteurs = []
    scrutins = []
    votes = []

    if "acteurs" in datasets:
        acteurs = parse_all_acteurs(datasets["acteurs"])

    if "scrutins" in datasets:
        scrutins, votes = parse_all_scrutins(datasets["scrutins"])

    # Step 3: Import to database
    logger.info("Step 3: Importing to PostgreSQL...")
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        if acteurs:
            import_deputes(session, acteurs)
        if scrutins:
            import_scrutins(session, scrutins, votes)

        logger.info("=== ETL Pipeline completed successfully ===")
    except Exception as e:
        session.rollback()
        logger.error(f"Import failed: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
