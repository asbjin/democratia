"""Pydantic schemas for groupes API."""

from pydantic import BaseModel
from .depute import DeputeResponse


class GroupeStats(BaseModel):
    id: str
    nom: str
    sigle: str | None = None
    couleur: str | None = None
    nb_membres: int = 0

    class Config:
        from_attributes = True


class GroupeDetail(GroupeStats):
    deputes: list[DeputeResponse] = []


class GroupeList(BaseModel):
    items: list[GroupeStats]
    total: int
