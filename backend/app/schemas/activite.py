# DemocratIA - Pydantic schemas for depute activity

import datetime
from typing import Optional, List

from pydantic import BaseModel, field_validator


class InterventionBrief(BaseModel):
    id: int
    date: Optional[datetime.date] = None
    texte: Optional[str] = None
    type_seance: Optional[str] = None

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v):
        if v is None:
            return None
        if isinstance(v, datetime.date):
            return v
        if isinstance(v, str):
            try:
                return datetime.date.fromisoformat(v)
            except ValueError:
                return None
        return None

    class Config:
        from_attributes = True


class VoteBrief(BaseModel):
    scrutin_id: str
    position: str
    scrutin_titre: Optional[str] = None
    scrutin_date: Optional[datetime.date] = None

    @field_validator("scrutin_date", mode="before")
    @classmethod
    def parse_scrutin_date(cls, v):
        if v is None:
            return None
        if isinstance(v, datetime.date):
            return v
        if isinstance(v, str):
            try:
                return datetime.date.fromisoformat(v)
            except ValueError:
                return None
        return None

    class Config:
        from_attributes = True


class AmendementBrief(BaseModel):
    id: str
    date: Optional[datetime.date] = None
    sort: Optional[str] = None
    objet: Optional[str] = None

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v):
        if v is None:
            return None
        if isinstance(v, datetime.date):
            return v
        if isinstance(v, str):
            try:
                return datetime.date.fromisoformat(v)
            except ValueError:
                return None
        return None

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
