"""Pydantic schemas for deputes API."""

from datetime import date
from pydantic import BaseModel


class GroupeResponse(BaseModel):
    id: str
    nom: str
    sigle: str | None = None
    couleur: str | None = None

    class Config:
        from_attributes = True


class DeputeResponse(BaseModel):
    id: str
    nom: str
    prenom: str
    date_naissance: date | None = None
    sexe: str | None = None
    profession: str | None = None
    groupe_politique_id: str | None = None
    circonscription: str | None = None
    departement: str | None = None
    photo_url: str | None = None

    class Config:
        from_attributes = True


class DeputeList(BaseModel):
    items: list[DeputeResponse]
    total: int
    page: int
    size: int
