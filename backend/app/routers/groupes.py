# DemocratIA - Groupes politiques API endpoints

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.groupe import Groupe
from ..models.depute import Depute
from ..models.intervention import Intervention
from ..models.amendement import Amendement
from ..models.vote import Vote
from ..models.scrutin import Scrutin
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


@router.get("/groupes/{groupe_id}/dashboard")
def get_groupe_dashboard(
    groupe_id: str,
    theme: str | None = None,
    db: Session = Depends(get_db),
):
    groupe = db.query(Groupe).filter(Groupe.id == groupe_id).first()
    if not groupe:
        raise HTTPException(status_code=404, detail="Groupe not found")

    # Get all depute IDs in this group
    membre_ids = [
        d.id for d in
        db.query(Depute.id).filter(Depute.groupe_politique_id == groupe_id).all()
    ]

    if not membre_ids:
        return {
            "groupe": {"id": groupe.id, "nom": groupe.nom, "sigle": groupe.sigle},
            "stats": {"nb_interventions": 0, "nb_amendements": 0},
            "cohesion": None,
            "top_deputes": [],
            "timeline": [],
        }

    # Stats: interventions and amendements
    intervention_query = db.query(func.count(Intervention.id)).filter(
        Intervention.depute_id.in_(membre_ids)
    )
    amendement_query = db.query(func.count(Amendement.id)).filter(
        Amendement.depute_id.in_(membre_ids)
    )

    if theme:
        intervention_query = intervention_query.filter(
            Intervention.search_vector.op("@@")(func.plainto_tsquery("french", theme))
        )
        amendement_query = amendement_query.filter(
            Amendement.objet.ilike(f"%{theme}%") | Amendement.texte.ilike(f"%{theme}%")
        )

    nb_interventions = intervention_query.scalar() or 0
    nb_amendements = amendement_query.scalar() or 0

    # Cohesion: percentage of votes where group members voted the same
    cohesion = None
    scrutin_votes = (
        db.query(
            Vote.scrutin_id,
            Vote.position,
            func.count(Vote.id).label("cnt"),
        )
        .filter(Vote.depute_id.in_(membre_ids))
        .group_by(Vote.scrutin_id, Vote.position)
        .all()
    )

    if scrutin_votes:
        # Group by scrutin_id, find majority position ratio
        scrutin_data: dict[str, dict[str, int]] = {}
        for row in scrutin_votes:
            if row.scrutin_id not in scrutin_data:
                scrutin_data[row.scrutin_id] = {}
            scrutin_data[row.scrutin_id][row.position] = row.cnt

        total_ratios = 0.0
        for positions in scrutin_data.values():
            total_votes_in_scrutin = sum(positions.values())
            if total_votes_in_scrutin > 0:
                majority = max(positions.values())
                total_ratios += majority / total_votes_in_scrutin

        if scrutin_data:
            cohesion = round((total_ratios / len(scrutin_data)) * 100, 1)

    # Top 5 deputes by intervention count
    top_deputes = (
        db.query(
            Depute.id,
            Depute.nom,
            Depute.prenom,
            Depute.departement,
            func.count(Intervention.id).label("nb_interventions"),
        )
        .join(Intervention, Intervention.depute_id == Depute.id)
        .filter(Depute.id.in_(membre_ids))
        .group_by(Depute.id)
        .order_by(func.count(Intervention.id).desc())
        .limit(5)
        .all()
    )

    # Monthly timeline
    timeline = (
        db.query(
            extract("year", Intervention.date).label("year"),
            extract("month", Intervention.date).label("month"),
            func.count(Intervention.id).label("count"),
        )
        .filter(Intervention.depute_id.in_(membre_ids))
        .filter(Intervention.date.isnot(None))
        .group_by("year", "month")
        .order_by("year", "month")
        .all()
    )

    return {
        "groupe": {"id": groupe.id, "nom": groupe.nom, "sigle": groupe.sigle},
        "stats": {
            "nb_interventions": nb_interventions,
            "nb_amendements": nb_amendements,
        },
        "cohesion": cohesion,
        "top_deputes": [
            {
                "id": d.id,
                "nom": d.nom,
                "prenom": d.prenom,
                "departement": d.departement,
                "nb_interventions": d.nb_interventions,
            }
            for d in top_deputes
        ],
        "timeline": [
            {
                "period": f"{int(t.year)}-{int(t.month):02d}",
                "count": t.count,
            }
            for t in timeline
        ],
    }
