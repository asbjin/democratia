# DemocratIA - Test data seeder

import json
import logging
import os
import random
import sys
from datetime import date, timedelta
from pathlib import Path

from sqlalchemy import create_engine, Column, String, Integer, Date, Text, ForeignKey
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

FIXTURES_PATH = Path(__file__).parent.parent / "fixtures" / "seed_data.json"


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
    profession = Column(String)
    groupe_politique_id = Column(String)
    circonscription = Column(String)
    departement = Column(String)


class Dossier(Base):
    __tablename__ = "dossiers"
    id = Column(String, primary_key=True)
    titre = Column(String, nullable=False)
    theme = Column(String)
    statut = Column(String)
    legislature = Column(Integer)


class Scrutin(Base):
    __tablename__ = "scrutins"
    id = Column(String, primary_key=True)
    dossier_id = Column(String, nullable=True)
    titre = Column(Text)
    date = Column(Date)
    nb_pour = Column(Integer, default=0)
    nb_contre = Column(Integer, default=0)
    nb_abstention = Column(Integer, default=0)


class Vote(Base):
    __tablename__ = "votes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    scrutin_id = Column(String, ForeignKey("scrutins.id"), nullable=False)
    depute_id = Column(String, ForeignKey("deputes.id"), nullable=False)
    position = Column(String, nullable=False)


class Intervention(Base):
    __tablename__ = "interventions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    depute_id = Column(String, ForeignKey("deputes.id"), nullable=False)
    dossier_id = Column(String, nullable=True)
    date = Column(Date)
    texte = Column(Text)
    type_seance = Column(String)


def load_fixtures() -> dict:
    """Load seed data from JSON fixture file."""
    with open(FIXTURES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_interventions(data: dict, depute_ids: list[str]) -> list[dict]:
    """Generate intervention records from templates."""
    templates = data["intervention_templates"]
    themes = data["themes"]
    dossier_ids = [d["id"] for d in data["dossiers"]]
    types_seance = ["Seance publique", "Commission", "Questions au gouvernement"]

    interventions = []
    start_date = date(2024, 1, 15)

    for i in range(data.get("interventions_count", 200)):
        theme = random.choice(themes)
        template = random.choice(templates)
        texte = template.replace("{theme}", theme)
        intervention_date = start_date + timedelta(days=random.randint(0, 330))

        interventions.append({
            "depute_id": random.choice(depute_ids),
            "dossier_id": random.choice(dossier_ids),
            "date": intervention_date,
            "texte": texte,
            "type_seance": random.choice(types_seance),
        })

    return interventions


def generate_votes(data: dict, depute_ids: list[str]) -> list[dict]:
    """Generate vote records for each scrutin."""
    votes = []
    positions = ["pour", "contre", "abstention"]
    weights = [0.55, 0.35, 0.10]

    for scrutin in data["scrutins"]:
        # Each depute votes on roughly 70% of scrutins
        voters = random.sample(depute_ids, k=int(len(depute_ids) * 0.7))
        for depute_id in voters:
            position = random.choices(positions, weights=weights, k=1)[0]
            votes.append({
                "scrutin_id": scrutin["id"],
                "depute_id": depute_id,
                "position": position,
            })

    return votes


def seed(session):
    """Insert all fixture data into the database."""
    data = load_fixtures()

    # Groupes
    for g in data["groupes"]:
        if not session.get(Groupe, g["id"]):
            session.add(Groupe(**g))
    session.commit()
    logger.info(f"Seeded {len(data['groupes'])} groupes")

    # Deputes
    depute_ids = []
    for d in data["deputes"]:
        depute_ids.append(d["id"])
        if not session.get(Depute, d["id"]):
            session.add(Depute(**d))
    session.commit()
    logger.info(f"Seeded {len(data['deputes'])} deputes")

    # Dossiers
    for d in data["dossiers"]:
        if not session.get(Dossier, d["id"]):
            session.add(Dossier(**d))
    session.commit()
    logger.info(f"Seeded {len(data['dossiers'])} dossiers")

    # Scrutins
    for s in data["scrutins"]:
        if not session.get(Scrutin, s["id"]):
            s_copy = dict(s)
            if s_copy.get("date"):
                s_copy["date"] = date.fromisoformat(s_copy["date"])
            session.add(Scrutin(**s_copy))
    session.commit()
    logger.info(f"Seeded {len(data['scrutins'])} scrutins")

    # Interventions
    random.seed(42)
    interventions = generate_interventions(data, depute_ids)
    for interv in interventions:
        session.add(Intervention(**interv))
    session.commit()
    logger.info(f"Seeded {len(interventions)} interventions")

    # Votes
    votes = generate_votes(data, depute_ids)
    for v in votes:
        session.add(Vote(**v))
    session.commit()
    logger.info(f"Seeded {len(votes)} votes")


def main():
    logger.info("=== Seeding test data ===")

    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        seed(session)
        logger.info("=== Seeding completed successfully ===")
    except Exception as e:
        session.rollback()
        logger.error(f"Seeding failed: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
