"""Pydantic schemas for scrutins API."""

from datetime import date
from pydantic import BaseModel


class VoteGroupe(BaseModel):
    groupe_id: str | None = None
    groupe_nom: str | None = None
    pour: int = 0
    contre: int = 0
    abstention: int = 0


class ScrutinResponse(BaseModel):
    id: str
    date: date | None = None
    titre: str | None = None
    nb_pour: int = 0
    nb_contre: int = 0
    nb_abstention: int = 0
    dossier_id: str | None = None

    class Config:
        from_attributes = True


class ScrutinDetail(ScrutinResponse):
    votes_par_groupe: list[VoteGroupe] = []


class ScrutinList(BaseModel):
    items: list[ScrutinResponse]
    total: int
    page: int
    size: int
