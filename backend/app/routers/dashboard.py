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
        # Build the theme filter for interventions (ILIKE on texte)
        theme_filter = Intervention.texte.ilike(f"%{theme}%") if theme else None

        # --- Top 10 deputies who talk about this theme ---
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
        if theme_filter is not None:
            top_query = top_query.filter(theme_filter)
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

        # --- Activity by group (deputies who talked about this theme) ---
        par_groupe_query = (
            db.query(
                Groupe.nom,
                Groupe.sigle,
                func.count(func.distinct(Depute.id)).label("count"),
            )
            .join(Depute, Depute.groupe_politique_id == Groupe.id)
            .join(Intervention, Intervention.depute_id == Depute.id)
        )
        if theme_filter is not None:
            par_groupe_query = par_groupe_query.filter(theme_filter)
        if departement:
            par_groupe_query = par_groupe_query.filter(Depute.departement.ilike(f"%{departement}%"))

        par_groupe = par_groupe_query.group_by(Groupe.id, Groupe.nom, Groupe.sigle).all()

        par_groupe_list = [
            {
                "groupe": g.nom or "Sans groupe",
                "sigle": g.sigle or "",
                "count": g.count,
            }
            for g in par_groupe
        ]

        # --- Timeline (interventions per month, filtered by theme) ---
        timeline_list = []
        try:
            tl_query = (
                db.query(
                    extract("year", Intervention.date).label("year"),
                    extract("month", Intervention.date).label("month"),
                    func.count(Intervention.id).label("count"),
                )
                .filter(Intervention.date.isnot(None))
            )
            if theme_filter is not None:
                tl_query = tl_query.filter(theme_filter)

            timeline = (
                tl_query.group_by("year", "month")
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
        except Exception:
            db.rollback()
            logger.warning("Failed to fetch timeline data")

        # --- Stats (all filtered by theme + departement) ---
        if theme:
            interv_q = db.query(Intervention).filter(Intervention.texte.ilike(f"%{theme}%"))
            if departement:
                interv_q = interv_q.join(Depute, Depute.id == Intervention.depute_id).filter(
                    Depute.departement.ilike(f"%{departement}%")
                )
            nb_interventions = interv_q.count()

            dep_q = (
                db.query(func.count(func.distinct(Intervention.depute_id)))
                .filter(Intervention.texte.ilike(f"%{theme}%"))
            )
            if departement:
                dep_q = dep_q.join(Depute, Depute.id == Intervention.depute_id).filter(
                    Depute.departement.ilike(f"%{departement}%")
                )
            nb_deputes = dep_q.scalar() or 0

            nb_scrutins = db.query(func.count(Scrutin.id)).filter(
                Scrutin.titre.ilike(f"%{theme}%")
            ).scalar() or 0
        else:
            depute_query = db.query(Depute)
            if departement:
                depute_query = depute_query.filter(Depute.departement.ilike(f"%{departement}%"))
            nb_deputes = depute_query.count()
            nb_interventions = db.query(func.count(Intervention.id)).scalar() or 0
            nb_scrutins = db.query(func.count(Scrutin.id)).scalar() or 0

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
        query = (
            db.query(
                Depute.departement,
                func.count(func.distinct(Depute.id)).label("nb_deputes_actifs"),
                func.count(Intervention.id).label("nb_interventions"),
            )
            # Outer join: a department must still appear on the map even when it
            # has deputies but no interventions yet (e.g. real data without CR).
            .outerjoin(Intervention, Intervention.depute_id == Depute.id)
            .filter(Depute.departement.isnot(None))
        )

        if theme:
            query = query.filter(Intervention.texte.ilike(f"%{theme}%"))

        query = query.group_by(Depute.departement)
        results = query.all()

        geo_data = []
        for r in results:
            top = (
                db.query(Depute.nom, Depute.prenom)
                .outerjoin(Intervention, Intervention.depute_id == Depute.id)
                .filter(Depute.departement == r.departement)
                .group_by(Depute.id, Depute.nom, Depute.prenom)
                .order_by(func.count(Intervention.id).desc())
                .first()
            )
            geo_data.append({
                "departement": r.departement,
                "nom": r.departement,
                "nb_deputes_actifs": r.nb_deputes_actifs,
                "nb_interventions": r.nb_interventions,
                "top_depute": f"{top.prenom} {top.nom}" if top else None,
            })

        _set_cached(cache_key, geo_data)
        return geo_data

    except Exception as e:
        db.rollback()
        logger.error(f"GET /dashboard/geo failed: {e}")
        return []
