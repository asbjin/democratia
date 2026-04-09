# DemocratIA - Vote model

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base


class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scrutin_id = Column(String, ForeignKey("scrutins.id"), nullable=False)
    depute_id = Column(String, ForeignKey("deputes.id"), nullable=False)
    position = Column(String, nullable=False)  # pour, contre, abstention

    scrutin = relationship("Scrutin", back_populates="votes")
    depute = relationship("Depute", back_populates="votes")
