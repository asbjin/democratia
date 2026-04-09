# DemocratIA - Scrutins API endpoints

from typing import Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.scrutin import Scrutin
from ..models.vote import Vote
from ..models.depute import Depute
from ..models.groupe import Groupe
from ..schemas.scrutin import ScrutinResponse, ScrutinDetail, ScrutinList, VoteGroupe

router = APIRouter()


@router.get("/scrutins", response_model=ScrutinList)
def list_scrutins(
    theme: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Scrutin)

    if theme:
        query = query.filter(Scrutin.titre.ilike(f"%{theme}%"))

    total = query.count()
    items = query.order_by(Scrutin.date.desc()).offset((page - 1) * size).limit(size).all()

    return ScrutinList(items=items, total=total, page=page, size=size)


@router.get("/scrutins/{scrutin_id}", response_model=ScrutinDetail)
def get_scrutin(scrutin_id: str, db: Session = Depends(get_db)):
    scrutin = db.query(Scrutin).filter(Scrutin.id == scrutin_id).first()
    if not scrutin:
        raise HTTPException(status_code=404, detail="Scrutin not found")

    # Votes breakdown by group
    votes_par_groupe = (
        db.query(
            Depute.groupe_politique_id,
            Vote.position,
            func.count(Vote.id).label("count"),
        )
        .join(Depute, Depute.id == Vote.depute_id)
        .filter(Vote.scrutin_id == scrutin_id)
        .group_by(Depute.groupe_politique_id, Vote.position)
        .all()
    )

    # Aggregate by group
    groupes_dict: Dict[str, dict] = {}
    for row in votes_par_groupe:
        gid = row.groupe_politique_id or "Sans groupe"
        if gid not in groupes_dict:
            groupe = db.query(Groupe).filter(Groupe.id == gid).first()
            groupes_dict[gid] = {
                "groupe_id": gid,
                "groupe_nom": groupe.nom if groupe else gid,
                "pour": 0,
                "contre": 0,
                "abstention": 0,
            }
        groupes_dict[gid][row.position] = row.count

    return ScrutinDetail(
        id=scrutin.id,
        date=scrutin.date,
        titre=scrutin.titre,
        nb_pour=scrutin.nb_pour,
        nb_contre=scrutin.nb_contre,
        nb_abstention=scrutin.nb_abstention,
        dossier_id=scrutin.dossier_id,
        votes_par_groupe=[VoteGroupe(**v) for v in groupes_dict.values()],
    )
