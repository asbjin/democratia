"""Deputes API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.depute import Depute
from ..schemas.depute import DeputeResponse, DeputeList

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
