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
from ..models.vote import Vote

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
            # --- Theme mode: aggregate from scrutins (title) + their votes ---
            # A depute is "active on the theme" if they voted on a matching scrutin.

            # Top 10 deputies by number of votes cast on theme-matching scrutins
            top_query = (
                db.query(
                    Depute.id,
                    Depute.nom,
                    Depute.prenom,
                    Depute.groupe_politique_id,
                    Depute.departement,
                    func.count(Vote.id).label("nb"),
                )
                .join(Vote, Vote.depute_id == Depute.id)
                .join(Scrutin, Scrutin.id == Vote.scrutin_id)
                .filter(Scrutin.titre.ilike(theme_like))
            )
            if departement:
                top_query = top_query.filter(Depute.departement.ilike(f"%{departement}%"))
            top_deputes = (
                top_query.group_by(Depute.id)
                .order_by(func.count(Vote.id).desc())
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

            # Distinct deputies per group who voted on theme-matching scrutins
            par_groupe_query = (
                db.query(
                    Groupe.nom,
                    Groupe.sigle,
                    func.count(func.distinct(Depute.id)).label("count"),
                )
                .join(Depute, Depute.groupe_politique_id == Groupe.id)
                .join(Vote, Vote.depute_id == Depute.id)
                .join(Scrutin, Scrutin.id == Vote.scrutin_id)
                .filter(Scrutin.titre.ilike(theme_like))
            )
            if departement:
                par_groupe_query = par_groupe_query.filter(
                    Depute.departement.ilike(f"%{departement}%")
                )
            par_groupe = par_groupe_query.group_by(Groupe.id, Groupe.nom, Groupe.sigle).all()

            timeline_list = _scrutin_timeline(db, theme_like)

            nb_scrutins = (
                db.query(func.count(Scrutin.id))
                .filter(Scrutin.titre.ilike(theme_like))
                .scalar()
                or 0
            )
            nb_dep_q = (
                db.query(func.count(func.distinct(Depute.id)))
                .join(Vote, Vote.depute_id == Depute.id)
                .join(Scrutin, Scrutin.id == Vote.scrutin_id)
                .filter(Scrutin.titre.ilike(theme_like))
            )
            if departement:
                nb_dep_q = nb_dep_q.filter(Depute.departement.ilike(f"%{departement}%"))
            nb_deputes = nb_dep_q.scalar() or 0
            nb_interventions = 0

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

            depute_query = db.query(Depute)
            if departement:
                depute_query = depute_query.filter(Depute.departement.ilike(f"%{departement}%"))
            nb_deputes = depute_query.count()
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
            # Theme mode: deputies per department active on matching scrutins (votes)
            query = (
                db.query(
                    Depute.departement,
                    func.count(func.distinct(Depute.id)).label("nb_deputes_actifs"),
                    func.count(Vote.id).label("nb_interventions"),
                )
                .join(Vote, Vote.depute_id == Depute.id)
                .join(Scrutin, Scrutin.id == Vote.scrutin_id)
                .filter(Depute.departement.isnot(None))
                .filter(Scrutin.titre.ilike(theme_like))
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
                # In theme mode this holds the vote count on matching scrutins; the
                # map colours by nb_deputes_actifs when interventions are absent.
                "nb_interventions": 0,
                "top_depute": f"{top.prenom} {top.nom}" if top else None,
            })

        _set_cached(cache_key, geo_data)
        return geo_data

    except Exception as e:
        db.rollback()
        logger.error(f"GET /dashboard/geo failed: {e}")
        return []
