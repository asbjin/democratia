# DemocratIA - Pydantic schemas for deputes

from datetime import date
from typing import Optional

from pydantic import BaseModel


class GroupeResponse(BaseModel):
    id: str
    nom: str
    sigle: Optional[str] = None
    couleur: Optional[str] = None

    class Config:
        from_attributes = True


class DeputeResponse(BaseModel):
    id: str
    nom: str
    prenom: str
    date_naissance: Optional[date] = None
    sexe: Optional[str] = None
    profession: Optional[str] = None
    groupe_politique_id: Optional[str] = None
    circonscription: Optional[str] = None
    departement: Optional[str] = None
    photo_url: Optional[str] = None

    class Config:
        from_attributes = True


class DeputeList(BaseModel):
    items: list[DeputeResponse]
    total: int
    page: int
    size: int
