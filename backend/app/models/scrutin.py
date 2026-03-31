"""Scrutin model."""

from sqlalchemy import Column, String, Integer, Date, Text, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base


class Scrutin(Base):
    __tablename__ = "scrutins"

    id = Column(String, primary_key=True)
    dossier_id = Column(String, ForeignKey("dossiers.id"), nullable=True)
    date = Column(Date)
    titre = Column(Text)
    nb_pour = Column(Integer, default=0)
    nb_contre = Column(Integer, default=0)
    nb_abstention = Column(Integer, default=0)

    dossier = relationship("Dossier", backref="scrutins")
    votes = relationship("Vote", back_populates="scrutin")
