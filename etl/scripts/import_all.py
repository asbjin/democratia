# DemocratIA - ETL pipeline orchestrator

import logging
import os
import sys

from sqlalchemy import create_engine, Column, String, Integer, Date, Text, ForeignKey, text
from sqlalchemy.orm import declarative_base, sessionmaker

from download import download_all
from parse_acteurs import parse_all_acteurs, parse_all_groupes
from parse_scrutins import parse_all_scrutins
from parse_questions import parse_all_questions
from parse_amendements import parse_all_amendements
from parse_comptes_rendus import parse_all_comptes_rendus
from import_photos import import_photos

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


class Groupe(Base):
    __tablename__ = "groupes"

    id = Column(String, primary_key=True)
    nom = Column(String, nullable=False)
    sigle = Column(String)
    couleur = Column(String)


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


class Question(Base):
    __tablename__ = "questions"

    id = Column(String, primary_key=True)
    depute_id = Column(String, ForeignKey("deputes.id"), nullable=False)
    date = Column(String)
    theme = Column(String)
    texte = Column(Text)
    reponse = Column(Text)
    ministere = Column(String)


class Amendement(Base):
    __tablename__ = "amendements"

    id = Column(String, primary_key=True)
    depute_id = Column(String, ForeignKey("deputes.id"), nullable=False)
    dossier_id = Column(String, nullable=True)
    texte = Column(Text)
    sort = Column(String)
    date = Column(String)
    objet = Column(Text)


def import_groupes(session, groupes: list[dict]):
    """Insert political groups (parents of deputes via FK)."""
    count = 0
    for g in groupes:
        if session.get(Groupe, g["id"]) is None:
            session.add(Groupe(
                id=g["id"],
                nom=g["nom"],
                sigle=g.get("sigle", ""),
                couleur=g.get("couleur", ""),
            ))
            count += 1

    session.commit()
    logger.info(f"Imported {count} new groupes")


class Intervention(Base):
    __tablename__ = "interventions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    depute_id = Column(String, ForeignKey("deputes.id"), nullable=False)
    dossier_id = Column(String, nullable=True)
    date = Column(String)
    texte = Column(Text)
    type_seance = Column(String)
    # search_vector (tsvector) is populated by a raw SQL UPDATE after insert.


def import_deputes(session, acteurs: list[dict]):
    """Insert or update deputes."""
    count = 0
    for acteur in acteurs:
        depute = session.get(Depute, acteur["uid"])
        if depute is None:
            # Empty date/group would violate DATE / FK constraints -> use None
            depute = Depute(
                id=acteur["uid"],
                nom=acteur["nom"],
                prenom=acteur["prenom"],
                date_naissance=acteur.get("dateNaissance") or None,
                sexe=acteur.get("sexe", ""),
                groupe_politique_id=acteur.get("groupe_politique") or None,
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
                date=s["date"] or None,
                nb_pour=s["nb_pour"],
                nb_contre=s["nb_contre"],
                nb_abstention=s["nb_abstention"],
                # dossier_id kept null: dossiers are not imported by this pipeline,
                # so a real dossierRef would violate the scrutins->dossiers FK.
                dossier_id=None,
            )
            session.add(scrutin)
            scrutin_count += 1

    session.commit()
    logger.info(f"Imported {scrutin_count} new scrutins")

    # Import votes (only for deputes that exist), bulk-inserted for volume
    existing_depute_ids = {d.id for d in session.query(Depute.id).all()}
    batch = []
    vote_count = 0
    for v in votes:
        if v["depute_id"] in existing_depute_ids:
            batch.append({
                "scrutin_id": v["scrutin_id"],
                "depute_id": v["depute_id"],
                "position": v["position"],
            })
            vote_count += 1

            if len(batch) >= 5000:
                session.bulk_insert_mappings(Vote, batch)
                session.commit()
                batch = []
                logger.info(f"  ... {vote_count} votes imported so far")

    if batch:
        session.bulk_insert_mappings(Vote, batch)
        session.commit()
    logger.info(f"Imported {vote_count} votes")


def import_questions(session, questions: list[dict]):
    """Insert questions, skipping duplicates by ID."""
    existing_depute_ids = {d.id for d in session.query(Depute.id).all()}
    count = 0
    for q in questions:
        if q["depute_id"] not in existing_depute_ids:
            continue
        existing = session.get(Question, q["id"])
        if existing is not None:
            continue
        question = Question(
            id=q["id"],
            depute_id=q["depute_id"],
            date=q.get("date", ""),
            theme=q.get("theme", ""),
            texte=q.get("texte", ""),
            reponse=q.get("reponse", ""),
            ministere=q.get("ministere", ""),
        )
        session.add(question)
        count += 1

        if count % 1000 == 0:
            session.commit()
            logger.info(f"  ... {count} questions imported so far")

    session.commit()
    logger.info(f"Imported {count} new questions")


def import_amendements(session, amendements: list[dict]):
    """Insert amendements, skipping duplicates by ID."""
    existing_depute_ids = {d.id for d in session.query(Depute.id).all()}
    count = 0
    for a in amendements:
        if a["depute_id"] not in existing_depute_ids:
            continue
        existing = session.get(Amendement, a["id"])
        if existing is not None:
            continue
        amendement = Amendement(
            id=a["id"],
            depute_id=a["depute_id"],
            dossier_id=a.get("dossier_id", ""),
            texte=a.get("texte", ""),
            sort=a.get("sort", ""),
            date=a.get("date", ""),
            objet=a.get("objet", ""),
        )
        session.add(amendement)
        count += 1

        if count % 1000 == 0:
            session.commit()
            logger.info(f"  ... {count} amendements imported so far")

    session.commit()
    logger.info(f"Imported {count} new amendements")


def import_interventions(session, interventions: list[dict]):
    """Insert interventions (speeches) for known deputes, then build the FTS vector."""
    existing_depute_ids = {d.id for d in session.query(Depute.id).all()}
    batch = []
    count = 0
    for it in interventions:
        if it["depute_id"] not in existing_depute_ids or not it.get("date"):
            continue
        batch.append({
            "depute_id": it["depute_id"],
            "date": it["date"],
            "texte": it["texte"],
            "type_seance": it.get("type_seance", ""),
        })
        count += 1
        if len(batch) >= 5000:
            session.bulk_insert_mappings(Intervention, batch)
            session.commit()
            batch = []
            logger.info(f"  ... {count} interventions imported so far")

    if batch:
        session.bulk_insert_mappings(Intervention, batch)
        session.commit()
    logger.info(f"Imported {count} interventions")

    # Populate the full-text search vector (matches search.py: french + unaccent)
    logger.info("Building full-text search vectors...")
    session.execute(text(
        "UPDATE interventions "
        "SET search_vector = to_tsvector('french', unaccent(coalesce(texte, ''))) "
        "WHERE search_vector IS NULL"
    ))
    session.commit()


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
    groupes = []
    scrutins = []
    votes = []
    questions = []
    amendements = []
    interventions = []

    if "acteurs" in datasets:
        acteurs = parse_all_acteurs(datasets["acteurs"])
        # Keep only the groups actually referenced by a depute (FK parents)
        referenced = {a["groupe_politique"] for a in acteurs if a["groupe_politique"]}
        groupes = [g for g in parse_all_groupes(datasets["acteurs"]) if g["id"] in referenced]

    if "scrutins" in datasets:
        scrutins, votes = parse_all_scrutins(datasets["scrutins"])

    if "questions" in datasets:
        questions = parse_all_questions(datasets["questions"])

    if "amendements" in datasets:
        amendements = parse_all_amendements(datasets["amendements"])

    if "comptes_rendus" in datasets:
        interventions = parse_all_comptes_rendus(datasets["comptes_rendus"])

    # Step 3: Import to database
    logger.info("Step 3: Importing to PostgreSQL...")
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        if groupes:
            import_groupes(session, groupes)
        if acteurs:
            import_deputes(session, acteurs)
        if scrutins:
            import_scrutins(session, scrutins, votes)
        if questions:
            import_questions(session, questions)
        if amendements:
            import_amendements(session, amendements)
        if interventions:
            import_interventions(session, interventions)

        # Step 4: Download deputy photos
        logger.info("Step 4: Downloading deputy photos...")
        try:
            import_photos()
        except Exception as e:
            logger.warning(f"Photo import failed (non-fatal): {e}")

        # Step 5: Print global stats
        logger.info("Step 5: Database statistics")
        nb_groupes = session.query(Groupe).count()
        nb_deputes = session.query(Depute).count()
        nb_scrutins_db = session.query(Scrutin).count()
        nb_votes = session.query(Vote).count()
        nb_questions = session.query(Question).count()
        nb_amendements = session.query(Amendement).count()
        nb_interventions = session.query(Intervention).count()
        logger.info(f"  Groupes:      {nb_groupes}")
        logger.info(f"  Deputes:      {nb_deputes}")
        logger.info(f"  Scrutins:     {nb_scrutins_db}")
        logger.info(f"  Votes:        {nb_votes}")
        logger.info(f"  Questions:    {nb_questions}")
        logger.info(f"  Amendements:  {nb_amendements}")
        logger.info(f"  Interventions:{nb_interventions}")

        logger.info("=== ETL Pipeline completed successfully ===")
    except Exception as e:
        session.rollback()
        logger.error(f"Import failed: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
