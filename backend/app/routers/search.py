"""Full-text search endpoint."""

import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from ..database import get_db
from ..models.intervention import Intervention
from ..models.depute import Depute
from ..services.synonyms import get_tsquery_expanded

router = APIRouter()


@router.get("/search")
def search_interventions(
    q: str = Query(..., min_length=2),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    logger.info(f"GET /search q={q} page={page}")
    # Expand query with parliamentary synonyms
    expanded = get_tsquery_expanded(q)
    ts_query = func.to_tsquery("french", func.unaccent(expanded.replace(" ", " & ")))

    query = (
        db.query(
            Intervention,
            Depute.nom,
            Depute.prenom,
            Depute.groupe_politique_id,
            func.ts_rank(Intervention.search_vector, ts_query).label("rank"),
        )
        .join(Depute, Intervention.depute_id == Depute.id)
        .filter(Intervention.search_vector.op("@@")(ts_query))
        .order_by(text("rank DESC"))
    )

    total = query.count()
    results = query.offset((page - 1) * size).limit(size).all()

    items = []
    for intervention, nom, prenom, groupe, rank in results:
        items.append({
            "id": intervention.id,
            "date": str(intervention.date) if intervention.date else None,
            "texte": intervention.texte[:500] if intervention.texte else "",
            "type_seance": intervention.type_seance,
            "depute": {
                "id": intervention.depute_id,
                "nom": nom,
                "prenom": prenom,
                "groupe_politique_id": groupe,
            },
            "score": round(float(rank), 4),
        })

    return {"items": items, "total": total, "page": page, "size": size}
