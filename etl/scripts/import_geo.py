"""Import geographic data: circonscriptions and department mapping."""

import logging
import os

from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
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


class Circonscription(Base):
    __tablename__ = "circonscriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, unique=True, nullable=False)
    departement = Column(String, nullable=False)
    region = Column(String, nullable=False)
    num_circo = Column(Integer)


# Mapping of departments to regions (metropolitan France)
DEPARTEMENT_REGIONS = {
    "Ain": "Auvergne-Rhone-Alpes",
    "Aisne": "Hauts-de-France",
    "Allier": "Auvergne-Rhone-Alpes",
    "Alpes-de-Haute-Provence": "Provence-Alpes-Cote d'Azur",
    "Hautes-Alpes": "Provence-Alpes-Cote d'Azur",
    "Alpes-Maritimes": "Provence-Alpes-Cote d'Azur",
    "Ardeche": "Auvergne-Rhone-Alpes",
    "Ardennes": "Grand Est",
    "Ariege": "Occitanie",
    "Aube": "Grand Est",
    "Aude": "Occitanie",
    "Aveyron": "Occitanie",
    "Bouches-du-Rhone": "Provence-Alpes-Cote d'Azur",
    "Calvados": "Normandie",
    "Cantal": "Auvergne-Rhone-Alpes",
    "Charente": "Nouvelle-Aquitaine",
    "Charente-Maritime": "Nouvelle-Aquitaine",
    "Cher": "Centre-Val de Loire",
    "Correze": "Nouvelle-Aquitaine",
    "Corse-du-Sud": "Corse",
    "Haute-Corse": "Corse",
    "Cote-d'Or": "Bourgogne-Franche-Comte",
    "Cotes-d'Armor": "Bretagne",
    "Creuse": "Nouvelle-Aquitaine",
    "Dordogne": "Nouvelle-Aquitaine",
    "Doubs": "Bourgogne-Franche-Comte",
    "Drome": "Auvergne-Rhone-Alpes",
    "Eure": "Normandie",
    "Eure-et-Loir": "Centre-Val de Loire",
    "Finistere": "Bretagne",
    "Gard": "Occitanie",
    "Haute-Garonne": "Occitanie",
    "Gers": "Occitanie",
    "Gironde": "Nouvelle-Aquitaine",
    "Herault": "Occitanie",
    "Ille-et-Vilaine": "Bretagne",
    "Indre": "Centre-Val de Loire",
    "Indre-et-Loire": "Centre-Val de Loire",
    "Isere": "Auvergne-Rhone-Alpes",
    "Jura": "Bourgogne-Franche-Comte",
    "Landes": "Nouvelle-Aquitaine",
    "Loir-et-Cher": "Centre-Val de Loire",
    "Loire": "Auvergne-Rhone-Alpes",
    "Haute-Loire": "Auvergne-Rhone-Alpes",
    "Loire-Atlantique": "Pays de la Loire",
    "Loiret": "Centre-Val de Loire",
    "Lot": "Occitanie",
    "Lot-et-Garonne": "Nouvelle-Aquitaine",
    "Lozere": "Occitanie",
    "Maine-et-Loire": "Pays de la Loire",
    "Manche": "Normandie",
    "Marne": "Grand Est",
    "Haute-Marne": "Grand Est",
    "Mayenne": "Pays de la Loire",
    "Meurthe-et-Moselle": "Grand Est",
    "Meuse": "Grand Est",
    "Morbihan": "Bretagne",
    "Moselle": "Grand Est",
    "Nievre": "Bourgogne-Franche-Comte",
    "Nord": "Hauts-de-France",
    "Oise": "Hauts-de-France",
    "Orne": "Normandie",
    "Pas-de-Calais": "Hauts-de-France",
    "Puy-de-Dome": "Auvergne-Rhone-Alpes",
    "Pyrenees-Atlantiques": "Nouvelle-Aquitaine",
    "Hautes-Pyrenees": "Occitanie",
    "Pyrenees-Orientales": "Occitanie",
    "Bas-Rhin": "Grand Est",
    "Haut-Rhin": "Grand Est",
    "Rhone": "Auvergne-Rhone-Alpes",
    "Haute-Saone": "Bourgogne-Franche-Comte",
    "Saone-et-Loire": "Bourgogne-Franche-Comte",
    "Sarthe": "Pays de la Loire",
    "Savoie": "Auvergne-Rhone-Alpes",
    "Haute-Savoie": "Auvergne-Rhone-Alpes",
    "Paris": "Ile-de-France",
    "Seine-Maritime": "Normandie",
    "Seine-et-Marne": "Ile-de-France",
    "Yvelines": "Ile-de-France",
    "Deux-Sevres": "Nouvelle-Aquitaine",
    "Somme": "Hauts-de-France",
    "Tarn": "Occitanie",
    "Tarn-et-Garonne": "Occitanie",
    "Var": "Provence-Alpes-Cote d'Azur",
    "Vaucluse": "Provence-Alpes-Cote d'Azur",
    "Vendee": "Pays de la Loire",
    "Vienne": "Nouvelle-Aquitaine",
    "Haute-Vienne": "Nouvelle-Aquitaine",
    "Vosges": "Grand Est",
    "Yonne": "Bourgogne-Franche-Comte",
    "Territoire de Belfort": "Bourgogne-Franche-Comte",
    "Essonne": "Ile-de-France",
    "Hauts-de-Seine": "Ile-de-France",
    "Seine-Saint-Denis": "Ile-de-France",
    "Val-de-Marne": "Ile-de-France",
    "Val-d'Oise": "Ile-de-France",
}

# Number of constituencies per department (approximate for major ones)
DEPT_CIRCOS = {
    "Paris": 18, "Nord": 21, "Bouches-du-Rhone": 16, "Rhone": 14,
    "Gironde": 12, "Hauts-de-Seine": 13, "Seine-Saint-Denis": 12,
    "Val-de-Marne": 11, "Yvelines": 12, "Essonne": 10,
    "Seine-et-Marne": 11, "Val-d'Oise": 10,
}


def import_circonscriptions(session):
    """Create circonscription records for all departments."""
    count = 0
    for dept, region in DEPARTEMENT_REGIONS.items():
        nb_circos = DEPT_CIRCOS.get(dept, 5)
        for num in range(1, nb_circos + 1):
            code = f"{dept}-{num}"
            existing = session.query(Circonscription).filter(
                Circonscription.code == code
            ).first()
            if existing:
                continue
            circo = Circonscription(
                code=code,
                departement=dept,
                region=region,
                num_circo=num,
            )
            session.add(circo)
            count += 1

    session.commit()
    logger.info(f"Imported {count} new circonscriptions")


def main():
    logger.info("=== Importing geographic data ===")

    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        import_circonscriptions(session)
        logger.info("=== Geographic import completed ===")
    except Exception as e:
        session.rollback()
        logger.error(f"Import failed: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
