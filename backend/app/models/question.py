"""Question au gouvernement model."""

from sqlalchemy import Column, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(String, primary_key=True)
    depute_id = Column(String, ForeignKey("deputes.id"), nullable=False)
    date = Column(Date)
    theme = Column(String)
    texte = Column(Text)
    reponse = Column(Text)
    ministere = Column(String)

    depute = relationship("Depute", back_populates="questions")
