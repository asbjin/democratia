# DemocratIA - Amendement model

from sqlalchemy import Column, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base


class Amendement(Base):
    __tablename__ = "amendements"

    id = Column(String, primary_key=True)
    depute_id = Column(String, ForeignKey("deputes.id"), nullable=False)
    dossier_id = Column(String, ForeignKey("dossiers.id"), nullable=False)
    texte = Column(Text)
    sort = Column(String)
    date = Column(Date)
    objet = Column(Text)

    depute = relationship("Depute", back_populates="amendements")
    dossier = relationship("Dossier", backref="amendements")
