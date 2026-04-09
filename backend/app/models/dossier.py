# DemocratIA - Dossier legislatif model

from sqlalchemy import Column, String, Date, Integer

from ..database import Base


class Dossier(Base):
    __tablename__ = "dossiers"

    id = Column(String, primary_key=True)
    titre = Column(String, nullable=False)
    theme = Column(String)
    date_depot = Column(Date)
    statut = Column(String)
    legislature = Column(Integer)
