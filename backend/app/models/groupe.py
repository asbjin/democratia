# DemocratIA - Groupe politique model

from sqlalchemy import Column, String

from ..database import Base


class Groupe(Base):
    __tablename__ = "groupes"

    id = Column(String, primary_key=True)
    nom = Column(String, nullable=False)
    sigle = Column(String)
    couleur = Column(String)
