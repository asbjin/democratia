# DemocratIA - Pydantic schemas for depute activity

from datetime import date
from pydantic import BaseModel


class InterventionBrief(BaseModel):
    id: int
    date: date | None = None
    texte: str | None = None
    type_seance: str | None = None

    class Config:
        from_attributes = True


class VoteBrief(BaseModel):
    scrutin_id: str
    position: str
    scrutin_titre: str | None = None
    scrutin_date: date | None = None

    class Config:
        from_attributes = True


class AmendementBrief(BaseModel):
    id: str
    date: date | None = None
    sort: str | None = None
    objet: str | None = None

    class Config:
        from_attributes = True


class ActiviteResponse(BaseModel):
    depute_id: str
    interventions: list[InterventionBrief]
    votes: list[VoteBrief]
    amendements: list[AmendementBrief]
    total_interventions: int
    total_votes: int
    total_amendements: int
