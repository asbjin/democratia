# DemocratIA - Dashboard aggregation endpoint with cache

import logging
import time
from typing import Optional, Dict, Tuple, Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, extract, text
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.depute import Depute
from ..models.groupe import Groupe
from ..models.intervention import Intervention
from ..models.scrutin import Scrutin

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory cache with TTL (5 minutes)
_cache: Dict[str, Tuple[float, Any]] = {}
_CACHE_TTL = 300  # seconds


def _get_cached(key: str):
    if key in _cache:
        ts, data = _cache[key]
        if time.time() - ts < _CACHE_TTL:
            return data
        del _cache[key]
    return None


def _set_cached(key: str, data) -> None:
    _cache[key] = (time.time(), data)


def _scrutin_timeline(db: Session, theme_like: Optional[str]):
    """Scrutins per month, optionally filtered by theme (title ILIKE)."""
    q = db.query(
        extract("year", Scrutin.date).label("year"),
        extract("month", Scrutin.date).label("month"),
        func.count(Scrutin.id).label("count"),
    ).filter(Scrutin.date.isnot(None))
    if theme_like:
        q = q.filter(Scrutin.titre.ilike(theme_like))
    rows = q.group_by("year", "month").order_by("year", "month").all()
    return [
        {"period": f"{int(r.year)}-{int(r.month):02d}", "count": r.count}
        for r in rows
    ]


@router.get("/dashboard")
def get_dashboard(
    theme: Optional[str] = None,
    departement: Optional[str] = None,
    db: Session = Depends(get_db),
):
    logger.info(f"GET /dashboard theme={theme} dept={departement}")
    cache_key = f"dashboard:{theme or ''}:{departement or ''}"
    cached = _get_cached(cache_key)
    if cached:
        return cached

    try:
        theme_like = f"%{theme}%" if theme else None

        if theme:
            # --- Theme mode: aggregate from interventions (speeches) on the theme ---
            theme_iv = Intervention.texte.ilike(theme_like)

            # Top 10 deputies by number of interventions mentioning the theme
            top_query = (
                db.query(
                    Depute.id,
                    Depute.nom,
                    Depute.prenom,
                    Depute.groupe_politique_id,
                    Depute.departement,
                    func.count(Intervention.id).label("nb"),
                )
                .join(Intervention, Intervention.depute_id == Depute.id)
                .filter(theme_iv)
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
                    "nb_interventions": d.nb,
                }
                for d in top_deputes
            ]

            # Distinct deputies per group who spoke about the theme
            par_groupe_query = (
                db.query(
                    Groupe.nom,
                    Groupe.sigle,
                    func.count(func.distinct(Depute.id)).label("count"),
                )
                .join(Depute, Depute.groupe_politique_id == Groupe.id)
                .join(Intervention, Intervention.depute_id == Depute.id)
                .filter(theme_iv)
            )
            if departement:
                par_groupe_query = par_groupe_query.filter(
                    Depute.departement.ilike(f"%{departement}%")
                )
            par_groupe = par_groupe_query.group_by(Groupe.id, Groupe.nom, Groupe.sigle).all()

            # Timeline: interventions on the theme, per month
            tl = (
                db.query(
                    extract("year", Intervention.date).label("year"),
                    extract("month", Intervention.date).label("month"),
                    func.count(Intervention.id).label("count"),
                )
                .filter(Intervention.date.isnot(None))
                .filter(theme_iv)
                .group_by("year", "month")
                .order_by("year", "month")
                .all()
            )
            timeline_list = [
                {"period": f"{int(t.year)}-{int(t.month):02d}", "count": t.count}
                for t in tl
            ]

            nb_iv_q = db.query(func.count(Intervention.id)).filter(theme_iv)
            nb_dep_q = db.query(
                func.count(func.distinct(Intervention.depute_id))
            ).filter(theme_iv)
            if departement:
                nb_iv_q = nb_iv_q.join(
                    Depute, Depute.id == Intervention.depute_id
                ).filter(Depute.departement.ilike(f"%{departement}%"))
                nb_dep_q = nb_dep_q.join(
                    Depute, Depute.id == Intervention.depute_id
                ).filter(Depute.departement.ilike(f"%{departement}%"))
            nb_interventions = nb_iv_q.scalar() or 0
            nb_deputes = nb_dep_q.scalar() or 0
            nb_scrutins = (
                db.query(func.count(Scrutin.id))
                .filter(Scrutin.titre.ilike(theme_like))
                .scalar()
                or 0
            )

        elif departement:
            # --- Department mode (no theme): activity of that department's deputies ---
            dep_like = f"%{departement}%"

            top_query = (
                db.query(
                    Depute.id, Depute.nom, Depute.prenom,
                    Depute.groupe_politique_id, Depute.departement,
                    func.count(Intervention.id).label("nb"),
                )
                .outerjoin(Intervention, Intervention.depute_id == Depute.id)
                .filter(Depute.departement.ilike(dep_like))
                .group_by(Depute.id)
                .order_by(func.count(Intervention.id).desc())
                .limit(10)
            )
            top_deputes_list = [
                {"id": d.id, "nom": d.nom, "prenom": d.prenom,
                 "groupe_politique_id": d.groupe_politique_id,
                 "departement": d.departement, "nb_interventions": d.nb}
                for d in top_query.all()
            ]

            par_groupe = (
                db.query(Groupe.nom, Groupe.sigle, func.count(func.distinct(Depute.id)).label("count"))
                .join(Depute, Depute.groupe_politique_id == Groupe.id)
                .filter(Depute.departement.ilike(dep_like))
                .group_by(Groupe.id, Groupe.nom, Groupe.sigle)
                .order_by(func.count(func.distinct(Depute.id)).desc())
                .all()
            )

            tl = (
                db.query(
                    extract("year", Intervention.date).label("year"),
                    extract("month", Intervention.date).label("month"),
                    func.count(Intervention.id).label("count"),
                )
                .join(Depute, Depute.id == Intervention.depute_id)
                .filter(Intervention.date.isnot(None))
                .filter(Depute.departement.ilike(dep_like))
                .group_by("year", "month").order_by("year", "month").all()
            )
            timeline_list = [
                {"period": f"{int(t.year)}-{int(t.month):02d}", "count": t.count} for t in tl
            ]

            nb_deputes = db.query(Depute).filter(Depute.departement.ilike(dep_like)).count()
            nb_interventions = (
                db.query(func.count(Intervention.id))
                .join(Depute, Depute.id == Intervention.depute_id)
                .filter(Depute.departement.ilike(dep_like))
                .scalar() or 0
            )
            nb_scrutins = db.query(func.count(Scrutin.id)).scalar() or 0

        else:
            # --- Default mode: party sizes + all scrutins timeline ---
            top_deputes_list = []
            par_groupe = (
                db.query(
                    Groupe.nom,
                    Groupe.sigle,
                    func.count(Depute.id).label("count"),
                )
                .outerjoin(Depute, Depute.groupe_politique_id == Groupe.id)
                .group_by(Groupe.id, Groupe.nom, Groupe.sigle)
                .order_by(func.count(Depute.id).desc())
                .all()
            )
            timeline_list = _scrutin_timeline(db, None)

            nb_deputes = db.query(Depute).count()
            nb_interventions = db.query(func.count(Intervention.id)).scalar() or 0
            nb_scrutins = db.query(func.count(Scrutin.id)).scalar() or 0

        par_groupe_list = [
            {
                "groupe": g.nom or "Sans groupe",
                "sigle": g.sigle or "",
                "count": g.count,
            }
            for g in par_groupe
        ]

        result = {
            "stats": {
                "nb_deputes": nb_deputes,
                "nb_interventions": nb_interventions,
                "nb_scrutins": nb_scrutins,
            },
            "top_deputes": top_deputes_list,
            "par_groupe": par_groupe_list,
            "timeline": timeline_list,
        }

        _set_cached(cache_key, result)
        return result

    except Exception as e:
        db.rollback()
        logger.error(f"GET /dashboard failed: {e}")
        return {
            "stats": {"nb_deputes": 0, "nb_interventions": 0, "nb_scrutins": 0},
            "top_deputes": [],
            "par_groupe": [],
            "timeline": [],
        }


@router.get("/dashboard/geo")
def get_dashboard_geo(
    theme: Optional[str] = None,
    db: Session = Depends(get_db),
):
    cache_key = f"geo:{theme or ''}"
    cached = _get_cached(cache_key)
    if cached:
        return cached

    try:
        theme_like = f"%{theme}%" if theme else None

        if theme:
            # Theme mode: interventions on the theme, per department (map heatmap)
            query = (
                db.query(
                    Depute.departement,
                    func.count(func.distinct(Depute.id)).label("nb_deputes_actifs"),
                    func.count(Intervention.id).label("nb_interventions"),
                )
                .join(Intervention, Intervention.depute_id == Depute.id)
                .filter(Depute.departement.isnot(None))
                .filter(Intervention.texte.ilike(theme_like))
                .group_by(Depute.departement)
            )
        else:
            # Default: all deputies per department (outer join keeps every dept)
            query = (
                db.query(
                    Depute.departement,
                    func.count(func.distinct(Depute.id)).label("nb_deputes_actifs"),
                    func.count(Intervention.id).label("nb_interventions"),
                )
                .outerjoin(Intervention, Intervention.depute_id == Depute.id)
                .filter(Depute.departement.isnot(None))
                .group_by(Depute.departement)
            )

        results = query.all()

        geo_data = []
        for r in results:
            top = (
                db.query(Depute.nom, Depute.prenom)
                .filter(Depute.departement == r.departement)
                .order_by(Depute.nom)
                .first()
            )
            geo_data.append({
                "departement": r.departement,
                "nom": r.departement,
                "nb_deputes_actifs": r.nb_deputes_actifs,
                # Theme mode: interventions on the theme (colours the heatmap).
                # Default mode: 0 so the map colours by number of deputies.
                "nb_interventions": r.nb_interventions if theme else 0,
                "top_depute": f"{top.prenom} {top.nom}" if top else None,
            })

        _set_cached(cache_key, geo_data)
        return geo_data

    except Exception as e:
        db.rollback()
        logger.error(f"GET /dashboard/geo failed: {e}")
        return []
