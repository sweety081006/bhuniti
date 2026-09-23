import json

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..models import Parcel

router = APIRouter(prefix="/api/gis", tags=["gis"])


@router.get("/layers")
def layers():
    """Layer catalogue for the GIS Studio.

    Bhuvan (ISRO) publishes open OGC/WMS endpoints that need no API key, so the
    satellite / thematic backdrop is real even though the parcels are synthetic.
    """
    return {
        "basemap": {
            "provider": "maptiler" if settings.maptiler_key else "osm",
            "maptiler_key_present": bool(settings.maptiler_key),
        },
        "wms": [
            {
                "id": "bhuvan_lulc",
                "name": "Land Use / Land Cover (Bhuvan, ISRO)",
                "url": "https://bhuvan-vec1.nrsc.gov.in/bhuvan/wms",
                "layers": "lulc:LULC50K_1516",
                "attribution": "ISRO / NRSC Bhuvan",
            },
        ],
        "vector": [
            {"id": "parcels", "name": "Cadastral parcels", "url": "/api/gis/parcels"},
        ],
        "note": "Parcel geometries are synthetic stand-ins for DILRMP/Bhunaksha data.",
    }


@router.get("/districts")
def districts(db: Session = Depends(get_db)):
    rows = (
        db.query(Parcel.district, func.count(Parcel.id), func.sum(Parcel.area_ha))
        .group_by(Parcel.district)
        .order_by(Parcel.district)
        .all()
    )
    return [
        {"district": d, "parcels": int(n), "area_ha": round(float(a or 0), 1)} for d, n, a in rows
    ]


@router.get("/parcels")
def parcels(
    district: str | None = None,
    land_use: str | None = None,
    dispute_status: str | None = None,
    climate_risk: str | None = None,
    limit: int = 2000,
    db: Session = Depends(get_db),
):
    """GeoJSON FeatureCollection for MapLibre."""
    q = db.query(Parcel)
    if district:
        q = q.filter(Parcel.district == district)
    if land_use:
        q = q.filter(Parcel.land_use == land_use)
    if dispute_status:
        q = q.filter(Parcel.dispute_status == dispute_status)
    if climate_risk:
        q = q.filter(Parcel.climate_risk == climate_risk)

    features = []
    for p in q.limit(limit).all():
        features.append(
            {
                "type": "Feature",
                "geometry": json.loads(p.geom_json),
                "properties": {
                    "parcel_uid": p.parcel_uid, "district": p.district, "block": p.block,
                    "village": p.village, "land_use": p.land_use, "area_ha": p.area_ha,
                    "owners": p.owners, "dispute_status": p.dispute_status,
                    "climate_risk": p.climate_risk, "source": p.source,
                },
            }
        )
    return {"type": "FeatureCollection", "features": features}
