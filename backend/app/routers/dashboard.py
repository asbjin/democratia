"""Dashboard aggregation endpoint."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.depute import Depute
from ..models.intervention import Intervention
from ..models.scrutin import Scrutin

router = APIRouter()


@router.get("/dashboard")
def get_dashboard(
    theme: str | None = None,
    departement: str | None = None,
    db: Session = Depends(get_db),
):
    # Base query for deputes
    depute_query = db.query(Depute)
    if departement:
        depute_query = depute_query.filter(Depute.departement.ilike(f"%{departement}%"))

    # Top 10 most active deputes (by intervention count)
    top_query = (
        db.query(
            Depute.id,
            Depute.nom,
            Depute.prenom,
            Depute.groupe_politique_id,
            Depute.departement,
            func.count(Intervention.id).label("nb_interventions"),
        )
        .join(Intervention, Intervention.depute_id == Depute.id)
    )
    if departement:
        top_query = top_query.filter(Depute.departement.ilike(f"%{departement}%"))
    top_deputes = (
        top_query.group_by(Depute.id)
        .order_by(func.count(Intervention.id).desc())
        .limit(10)
        .all()
    )

    top_deputes_list = [
        {
            "id": d.id,
            "nom": d.nom,
            "prenom": d.prenom,
            "groupe_politique_id": d.groupe_politique_id,
            "departement": d.departement,
            "nb_interventions": d.nb_interventions,
        }
        for d in top_deputes
    ]

    # Count by groupe politique
    par_groupe = (
        db.query(
            Depute.groupe_politique_id,
            func.count(Depute.id).label("count"),
        )
        .group_by(Depute.groupe_politique_id)
        .all()
    )

    par_groupe_list = [
        {"groupe": g.groupe_politique_id or "Sans groupe", "count": g.count}
        for g in par_groupe
    ]

    # Timeline: interventions per month
    timeline = (
        db.query(
            extract("year", Intervention.date).label("year"),
            extract("month", Intervention.date).label("month"),
            func.count(Intervention.id).label("count"),
        )
        .filter(Intervention.date.isnot(None))
        .group_by("year", "month")
        .order_by("year", "month")
        .all()
    )

    timeline_list = [
        {
            "period": f"{int(t.year)}-{int(t.month):02d}",
            "count": t.count,
        }
        for t in timeline
    ]

    # Stats
    nb_deputes = depute_query.count()
    nb_interventions = db.query(func.count(Intervention.id)).scalar() or 0
    nb_scrutins = db.query(func.count(Scrutin.id)).scalar() or 0

    return {
        "stats": {
            "nb_deputes": nb_deputes,
            "nb_interventions": nb_interventions,
            "nb_scrutins": nb_scrutins,
        },
        "top_deputes": top_deputes_list,
        "par_groupe": par_groupe_list,
        "timeline": timeline_list,
    }
