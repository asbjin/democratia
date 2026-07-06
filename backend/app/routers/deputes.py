# DemocratIA - Deputes API endpoints

import logging
from typing import Optional, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from ..database import get_db
from ..models.depute import Depute
from ..models.intervention import Intervention
from ..models.vote import Vote
from ..models.amendement import Amendement
from ..models.scrutin import Scrutin
from ..schemas.depute import DeputeResponse, DeputeList
from ..schemas.activite import ActiviteResponse, InterventionBrief, VoteBrief, AmendementBrief

# Neighboring departments mapping (simplified for major departments)
DEPT_NEIGHBORS: Dict[str, List[str]] = {
    "Paris": ["Hauts-de-Seine", "Seine-Saint-Denis", "Val-de-Marne"],
    "Hauts-de-Seine": ["Paris", "Yvelines", "Val-de-Marne", "Seine-Saint-Denis"],
    "Seine-Saint-Denis": ["Paris", "Hauts-de-Seine", "Val-de-Marne", "Val-d'Oise"],
    "Val-de-Marne": ["Paris", "Hauts-de-Seine", "Seine-Saint-Denis", "Essonne"],
    "Yvelines": ["Hauts-de-Seine", "Essonne", "Val-d'Oise"],
    "Essonne": ["Val-de-Marne", "Yvelines", "Seine-et-Marne"],
    "Nord": ["Pas-de-Calais", "Aisne", "Somme"],
    "Bouches-du-Rhone": ["Var", "Vaucluse", "Gard"],
    "Rhone": ["Ain", "Isere", "Loire"],
    "Gironde": ["Dordogne", "Lot-et-Garonne", "Landes", "Charente-Maritime"],
}

router = APIRouter()


@router.get("/deputes", response_model=DeputeList)
def list_deputes(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    groupe: Optional[str] = None,
    departement: Optional[str] = None,
    db: Session = Depends(get_db),
):
    logger.info(f"GET /deputes page={page} size={size} groupe={groupe} dept={departement}")
    query = db.query(Depute)

    if groupe:
        query = query.filter(Depute.groupe_politique_id == groupe)
    if departement:
        query = query.filter(Depute.departement.ilike(f"%{departement}%"))

    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    logger.info(f"GET /deputes returned {total} results")

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
    theme: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    depute = db.query(Depute).filter(Depute.id == depute_id).first()
    if not depute:
        raise HTTPException(status_code=404, detail="Depute not found")

    try:
        # Interventions with optional theme filter (ILIKE fallback if search_vector is empty)
        intervention_query = db.query(Intervention).filter(Intervention.depute_id == depute_id)
        if theme:
            try:
                intervention_query = intervention_query.filter(
                    Intervention.search_vector.op("@@")(func.plainto_tsquery("french", theme))
                )
                # Test the query to see if search_vector works
                intervention_query.count()
            except Exception:
                db.rollback()
                intervention_query = db.query(Intervention).filter(
                    Intervention.depute_id == depute_id,
                    Intervention.texte.ilike(f"%{theme}%"),
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

    except Exception as e:
        db.rollback()
        logger.error(f"GET /deputes/{depute_id}/activite failed: {e}")
        return ActiviteResponse(
            depute_id=depute_id,
            interventions=[],
            votes=[],
            amendements=[],
            total_interventions=0,
            total_votes=0,
            total_amendements=0,
        )


@router.get("/deputes/{depute_id}/votes")
def get_depute_votes(
    depute_id: str,
    theme: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    depute = db.query(Depute).filter(Depute.id == depute_id).first()
    if not depute:
        raise HTTPException(status_code=404, detail="Depute not found")

    # Use distinct on scrutin_id to avoid duplicates from seed data
    subquery = (
        db.query(
            Vote.scrutin_id,
            func.min(Vote.position).label("position"),
        )
        .filter(Vote.depute_id == depute_id)
        .group_by(Vote.scrutin_id)
        .subquery()
    )

    query = (
        db.query(
            subquery.c.scrutin_id,
            subquery.c.position,
            Scrutin.id,
            Scrutin.titre,
            Scrutin.date,
            Scrutin.nb_pour,
            Scrutin.nb_contre,
            Scrutin.nb_abstention,
        )
        .join(Scrutin, Scrutin.id == subquery.c.scrutin_id)
    )
    if theme:
        query = query.filter(
            func.unaccent(Scrutin.titre).ilike(func.unaccent(f"%{theme}%"))
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
                "scrutin_id": r.scrutin_id,
                "titre": r.titre,
                "date": r.date,
                "position": r.position,
                "nb_pour": r.nb_pour,
                "nb_contre": r.nb_contre,
                "nb_abstention": r.nb_abstention,
            }
            for r in results
        ],
    }


@router.get("/deputes/nearby")
def get_nearby_deputes(
    dept: str = Query(..., min_length=1),
    theme: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    neighbors = DEPT_NEIGHBORS.get(dept, [])
    all_depts = [dept] + neighbors

    query = db.query(Depute).filter(Depute.departement.in_(all_depts))

    if theme:
        depute_ids_with_theme = (
            db.query(Intervention.depute_id)
            .filter(Intervention.texte.ilike(f"%{theme}%"))
            .distinct()
            .subquery()
        )
        query = query.filter(Depute.id.in_(db.query(depute_ids_with_theme)))

    total = query.count()
    deputes = query.offset((page - 1) * size).limit(size).all()

    return {
        "departement": dept,
        "departements_inclus": all_depts,
        "total": total,
        "page": page,
        "size": size,
        "items": [
            {
                "id": d.id,
                "nom": d.nom,
                "prenom": d.prenom,
                "departement": d.departement,
                "groupe_politique_id": d.groupe_politique_id,
                "circonscription": d.circonscription,
            }
            for d in deputes
        ],
    }
