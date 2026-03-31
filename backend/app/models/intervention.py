"""Intervention model with full-text search."""

from sqlalchemy import Column, String, Integer, Date, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship

from ..database import Base


class Intervention(Base):
    __tablename__ = "interventions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    depute_id = Column(String, ForeignKey("deputes.id"), nullable=False)
    dossier_id = Column(String, ForeignKey("dossiers.id"), nullable=True)
    date = Column(Date)
    texte = Column(Text)
    type_seance = Column(String)
    search_vector = Column(TSVECTOR)

    depute = relationship("Depute", back_populates="interventions")
    dossier = relationship("Dossier", backref="interventions")

    __table_args__ = (
        Index("idx_intervention_search", "search_vector", postgresql_using="gin"),
    )
