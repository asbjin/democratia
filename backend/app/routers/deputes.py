"""Deputes API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.depute import Depute
from ..models.intervention import Intervention
from ..models.vote import Vote
from ..models.amendement import Amendement
from ..models.scrutin import Scrutin
from ..schemas.depute import DeputeResponse, DeputeList
from ..schemas.activite import ActiviteResponse, InterventionBrief, VoteBrief, AmendementBrief

router = APIRouter()


@router.get("/deputes", response_model=DeputeList)
def list_deputes(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    groupe: str | None = None,
    departement: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Depute)

    if groupe:
        query = query.filter(Depute.groupe_politique_id == groupe)
    if departement:
        query = query.filter(Depute.departement.ilike(f"%{departement}%"))

    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()

    return DeputeList(items=items, total=total, page=page, size=size)


@router.get("/deputes/{depute_id}", response_model=DeputeResponse)
def get_depute(depute_id: str, db: Session = Depends(get_db)):
    depute = db.query(Depute).filter(Depute.id == depute_id).first()
    if not depute:
        raise HTTPException(status_code=404, detail="Depute not found")
    return depute


@router.get("/deputes/{depute_id}/activite", response_model=ActiviteResponse)
def get_depute_activite(
    depute_id: str,
    theme: str | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    depute = db.query(Depute).filter(Depute.id == depute_id).first()
    if not depute:
        raise HTTPException(status_code=404, detail="Depute not found")

    # Interventions with optional full-text search
    intervention_query = db.query(Intervention).filter(Intervention.depute_id == depute_id)
    if theme:
        intervention_query = intervention_query.filter(
            Intervention.search_vector.op("@@")(func.plainto_tsquery("french", theme))
        )
    total_interventions = intervention_query.count()
    interventions = intervention_query.order_by(Intervention.date.desc()).offset((page - 1) * size).limit(size).all()

    # Votes
    vote_query = (
        db.query(Vote, Scrutin)
        .join(Scrutin, Scrutin.id == Vote.scrutin_id)
        .filter(Vote.depute_id == depute_id)
    )
    if theme:
        vote_query = vote_query.filter(Scrutin.titre.ilike(f"%{theme}%"))
    total_votes = vote_query.count()
    votes_raw = vote_query.order_by(Scrutin.date.desc()).offset((page - 1) * size).limit(size).all()

    # Amendements
    amendement_query = db.query(Amendement).filter(Amendement.depute_id == depute_id)
    if theme:
        amendement_query = amendement_query.filter(
            Amendement.objet.ilike(f"%{theme}%") | Amendement.texte.ilike(f"%{theme}%")
        )
    total_amendements = amendement_query.count()
    amendements = amendement_query.order_by(Amendement.date.desc()).offset((page - 1) * size).limit(size).all()

    return ActiviteResponse(
        depute_id=depute_id,
        interventions=[InterventionBrief.model_validate(i) for i in interventions],
        votes=[
            VoteBrief(
                scrutin_id=v.Vote.scrutin_id,
                position=v.Vote.position,
                scrutin_titre=v.Scrutin.titre,
                scrutin_date=v.Scrutin.date,
            )
            for v in votes_raw
        ],
        amendements=[AmendementBrief.model_validate(a) for a in amendements],
        total_interventions=total_interventions,
        total_votes=total_votes,
        total_amendements=total_amendements,
    )


@router.get("/deputes/{depute_id}/votes")
def get_depute_votes(
    depute_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    depute = db.query(Depute).filter(Depute.id == depute_id).first()
    if not depute:
        raise HTTPException(status_code=404, detail="Depute not found")

    query = (
        db.query(Vote, Scrutin)
        .join(Scrutin, Scrutin.id == Vote.scrutin_id)
        .filter(Vote.depute_id == depute_id)
    )
    total = query.count()
    results = query.order_by(Scrutin.date.desc()).offset((page - 1) * size).limit(size).all()

    return {
        "depute_id": depute_id,
        "total": total,
        "page": page,
        "size": size,
        "items": [
            {
                "scrutin_id": r.Scrutin.id,
                "titre": r.Scrutin.titre,
                "date": r.Scrutin.date,
                "position": r.Vote.position,
                "nb_pour": r.Scrutin.nb_pour,
                "nb_contre": r.Scrutin.nb_contre,
                "nb_abstention": r.Scrutin.nb_abstention,
            }
            for r in results
        ],
    }
