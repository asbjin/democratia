"""Cache models for IA results."""

from sqlalchemy import Column, String, Integer, Float, Text, DateTime
from sqlalchemy.sql import func

from ..database import Base


class ResumeCache(Base):
    __tablename__ = "resume_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    intervention_id = Column(String, unique=True, nullable=False, index=True)
    resume_text = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class SentimentCache(Base):
    __tablename__ = "sentiment_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    intervention_id = Column(String, nullable=False, index=True)
    theme = Column(String, default="")
    label = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    explanation = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())
