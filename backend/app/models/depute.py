# DemocratIA - Depute model

from sqlalchemy import Column, String, Date, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base


class Depute(Base):
    __tablename__ = "deputes"

    id = Column(String, primary_key=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    date_naissance = Column(Date, nullable=True)
    sexe = Column(String)
    profession = Column(String)
    groupe_politique_id = Column(String, ForeignKey("groupes.id"), nullable=True)
    circonscription = Column(String)
    departement = Column(String)
    photo_url = Column(String)

    groupe = relationship("Groupe", backref="deputes")
    interventions = relationship("Intervention", back_populates="depute")
    votes = relationship("Vote", back_populates="depute")
    questions = relationship("Question", back_populates="depute")
    amendements = relationship("Amendement", back_populates="depute")
