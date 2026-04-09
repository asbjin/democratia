# DemocratIA - Pydantic schemas for scrutins

from datetime import date
from typing import Optional

from pydantic import BaseModel


class VoteGroupe(BaseModel):
    groupe_id: Optional[str] = None
    groupe_nom: Optional[str] = None
    pour: int = 0
    contre: int = 0
    abstention: int = 0


class ScrutinResponse(BaseModel):
    id: str
    date: Optional[date] = None
    titre: Optional[str] = None
    nb_pour: int = 0
    nb_contre: int = 0
    nb_abstention: int = 0
    dossier_id: Optional[str] = None

    class Config:
        from_attributes = True


class ScrutinDetail(ScrutinResponse):
    votes_par_groupe: list[VoteGroupe] = []


class ScrutinList(BaseModel):
    items: list[ScrutinResponse]
    total: int
    page: int
    size: int
