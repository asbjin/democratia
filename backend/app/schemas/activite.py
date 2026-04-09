# DemocratIA - Pydantic schemas for depute activity

from datetime import date
from typing import Optional, List

from pydantic import BaseModel


class InterventionBrief(BaseModel):
    id: int
    date: Optional[date] = None
    texte: Optional[str] = None
    type_seance: Optional[str] = None

    class Config:
        from_attributes = True


class VoteBrief(BaseModel):
    scrutin_id: str
    position: str
    scrutin_titre: Optional[str] = None
    scrutin_date: Optional[date] = None

    class Config:
        from_attributes = True


class AmendementBrief(BaseModel):
    id: str
    date: Optional[date] = None
    sort: Optional[str] = None
    objet: Optional[str] = None

    class Config:
        from_attributes = True


class ActiviteResponse(BaseModel):
    depute_id: str
    interventions: List[InterventionBrief]
    votes: List[VoteBrief]
    amendements: List[AmendementBrief]
    total_interventions: int
    total_votes: int
    total_amendements: int
