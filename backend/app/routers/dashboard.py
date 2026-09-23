from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..models import DisputeStat, Document, Indicator, Parcel
from ..services import vectorstore

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    by_type = dict(
        db.query(Document.doc_type, func.count(Document.id)).group_by(Document.doc_type).all()
    )
    land_use = dict(
        db.query(Parcel.land_use, func.count(Parcel.id)).group_by(Parcel.land_use).all()
    )
    disputes = dict(
        db.query(Parcel.dispute_status, func.count(Parcel.id))
        .group_by(Parcel.dispute_status)
        .all()
    )
    try:
        chunks = vectorstore.count()
    except Exception:
        chunks = 0

    return {
        "pilot_state": settings.pilot_state,
        "documents": db.query(Document).count(),
        "documents_by_type": by_type,
        "indexed_chunks": chunks,
        "parcels": db.query(Parcel).count(),
        "parcels_by_land_use": land_use,
        "parcels_by_dispute_status": disputes,
        "districts": db.query(func.count(func.distinct(Parcel.district))).scalar() or 0,
    }


@router.get("/disputes")
def disputes(db: Session = Depends(get_db)):
    rows = (
        db.query(DisputeStat)
        .order_by(DisputeStat.district, DisputeStat.year)
        .all()
    )
    return [
        {
            "state": r.state, "district": r.district, "year": r.year,
            "pending_cases": r.pending_cases, "disposed_cases": r.disposed_cases,
            "avg_pendency_days": r.avg_pendency_days, "source": r.source,
        }
        for r in rows
    ]


@router.get("/indicators")
def indicators(name: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Indicator)
    if name:
        q = q.filter(Indicator.name == name)
    rows = q.order_by(Indicator.name, Indicator.year).all()
    return [
        {
            "name": r.name, "state": r.state, "district": r.district, "year": r.year,
            "value": r.value, "unit": r.unit, "source": r.source,
        }
        for r in rows
    ]
