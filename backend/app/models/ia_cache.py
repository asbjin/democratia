# DemocratIA - Cache models for IA results

from sqlalchemy import Column, String, Integer, Float, Text, DateTime, UniqueConstraint
from sqlalchemy.sql import func

from ..database import Base


class ResumeCache(Base):
    __tablename__ = "resume_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    intervention_id = Column(String, nullable=False, index=True)
    # Un resume peut etre generique ("") ou cible sur un theme recherche.
    theme = Column(String, default="")
    resume_text = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("intervention_id", "theme", name="uq_resume_intervention_theme"),
    )


class SentimentCache(Base):
    __tablename__ = "sentiment_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    intervention_id = Column(String, nullable=False, index=True)
    theme = Column(String, default="")
    label = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    explanation = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())
