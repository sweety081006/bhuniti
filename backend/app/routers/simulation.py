from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..db import get_db
from ..services import simulate

router = APIRouter(prefix="/api/simulation", tags=["policy-sandbox"])


class ScenarioRequest(BaseModel):
    district: str
    years: int = Field(default=5, ge=1, le=20)
    consolidation_rate: float | None = Field(default=None, ge=0.0, le=1.0)
    adoption_rate: float | None = Field(default=None, ge=0.0, le=1.0)
    dispute_elasticity: float | None = Field(default=None, ge=0.0, le=1.0)
    cost_per_ha: float | None = Field(default=None, ge=0.0)


@router.get("/defaults")
def defaults():
    return {
        "scenario": "land_consolidation",
        "assumptions": simulate.DEFAULTS,
        "explanation": {
            "consolidation_rate": "Share of eligible fragmented parcels consolidated each year.",
            "adoption_rate": "Share of landholders who participate in a voluntary scheme.",
            "dispute_elasticity": "How strongly consolidation reduces boundary/partition disputes.",
            "cost_per_ha": "Administrative and survey cost per hectare consolidated (INR).",
            "uncertainty": "Symmetric parameter uncertainty used to draw the band.",
        },
    }


@router.post("/run")
def run(req: ScenarioRequest, db: Session = Depends(get_db)):
    return simulate.run(
        db,
        district=req.district,
        years=req.years,
        consolidation_rate=req.consolidation_rate,
        adoption_rate=req.adoption_rate,
        dispute_elasticity=req.dispute_elasticity,
        cost_per_ha=req.cost_per_ha,
    )
