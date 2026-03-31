"""Groupes politiques API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.groupe import Groupe
from ..models.depute import Depute
from ..schemas.groupe import GroupeStats, GroupeDetail, GroupeList
from ..schemas.depute import DeputeResponse

router = APIRouter()


@router.get("/groupes", response_model=GroupeList)
def list_groupes(db: Session = Depends(get_db)):
    results = (
        db.query(
            Groupe,
            func.count(Depute.id).label("nb_membres"),
        )
        .outerjoin(Depute, Depute.groupe_politique_id == Groupe.id)
        .group_by(Groupe.id)
        .order_by(func.count(Depute.id).desc())
        .all()
    )

    items = [
        GroupeStats(
            id=r.Groupe.id,
            nom=r.Groupe.nom,
            sigle=r.Groupe.sigle,
            couleur=r.Groupe.couleur,
            nb_membres=r.nb_membres,
        )
        for r in results
    ]

    return GroupeList(items=items, total=len(items))


@router.get("/groupes/{groupe_id}", response_model=GroupeDetail)
def get_groupe(groupe_id: str, db: Session = Depends(get_db)):
    groupe = db.query(Groupe).filter(Groupe.id == groupe_id).first()
    if not groupe:
        raise HTTPException(status_code=404, detail="Groupe not found")

    deputes = db.query(Depute).filter(Depute.groupe_politique_id == groupe_id).all()
    nb_membres = len(deputes)

    return GroupeDetail(
        id=groupe.id,
        nom=groupe.nom,
        sigle=groupe.sigle,
        couleur=groupe.couleur,
        nb_membres=nb_membres,
        deputes=[DeputeResponse.model_validate(d) for d in deputes],
    )
