"""Policy Sandbox - land consolidation scenario (PS point 12).

This is a transparent, assumption-driven projection, NOT a prediction. Every
parameter is returned to the caller alongside the numbers, and every result
carries an uncertainty band, so a policymaker can see exactly what drives it.
"""

from dataclasses import dataclass

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models import DisputeStat, Parcel

# --- assumptions, all overridable from the API --------------------------------
DEFAULTS = {
    # share of eligible fragmented parcels actually consolidated each year
    "consolidation_rate": 0.15,
    # share of landholders who participate (voluntary schemes rarely hit 100%)
    "adoption_rate": 0.60,
    # how strongly consolidation translates into fewer boundary/partition disputes
    "dispute_elasticity": 0.45,
    # administrative + survey cost per hectare consolidated (INR)
    "cost_per_ha": 4200.0,
    # parameter uncertainty applied symmetrically to produce the band
    "uncertainty": 0.25,
}


@dataclass
class Baseline:
    district: str
    parcels: int
    total_area_ha: float
    avg_parcel_ha: float
    avg_owners: float
    fragmented_parcels: int
    pending_disputes: int


def baseline(db: Session, district: str) -> Baseline:
    q = db.query(
        func.count(Parcel.id),
        func.coalesce(func.sum(Parcel.area_ha), 0.0),
        func.coalesce(func.avg(Parcel.area_ha), 0.0),
        func.coalesce(func.avg(Parcel.owners), 1.0),
    ).filter(Parcel.district == district)
    n, total, avg_area, avg_owners = q.one()

    fragmented = (
        db.query(func.count(Parcel.id))
        .filter(Parcel.district == district, Parcel.area_ha < 1.0)
        .scalar()
        or 0
    )
    # latest year's pending count for the district (not a sum across years)
    latest = (
        db.query(DisputeStat)
        .filter(DisputeStat.district == district)
        .order_by(DisputeStat.year.desc())
        .first()
    )
    pending = latest.pending_cases if latest else 0
    return Baseline(
        district=district,
        parcels=int(n or 0),
        total_area_ha=round(float(total), 2),
        avg_parcel_ha=round(float(avg_area), 3),
        avg_owners=round(float(avg_owners), 2),
        fragmented_parcels=int(fragmented),
        pending_disputes=int(pending),
    )


def run(db: Session, district: str, years: int = 5, **overrides) -> dict:
    p = {**DEFAULTS, **{k: v for k, v in overrides.items() if v is not None}}
    base = baseline(db, district)

    if base.parcels == 0:
        return {
            "district": district,
            "error": "No parcels indexed for this district.",
            "baseline": base.__dict__,
            "assumptions": p,
            "series": [],
        }

    effective = p["consolidation_rate"] * p["adoption_rate"]
    unc = p["uncertainty"]

    series = []
    for t in range(0, years + 1):
        # share of originally-fragmented parcels that have been consolidated by year t
        done = 1 - (1 - effective) ** t

        avg_parcel = base.avg_parcel_ha * (1 + 0.6 * done)
        fragmented = base.fragmented_parcels * (1 - done)
        area_done = base.fragmented_parcels * base.avg_parcel_ha * done
        cost = area_done * p["cost_per_ha"]

        mid = base.pending_disputes * (1 - p["dispute_elasticity"] * done)
        low = base.pending_disputes * (1 - p["dispute_elasticity"] * (1 + unc) * done)
        high = base.pending_disputes * (1 - p["dispute_elasticity"] * (1 - unc) * done)

        series.append(
            {
                "year": t,
                "consolidated_share": round(done, 3),
                "avg_parcel_ha": round(avg_parcel, 3),
                "fragmented_parcels": int(round(fragmented)),
                "disputes_pending": int(round(mid)),
                "disputes_pending_low": int(round(max(0, low))),
                "disputes_pending_high": int(round(high)),
                "cumulative_cost_inr": round(cost, 0),
            }
        )

    final = series[-1]
    return {
        "district": district,
        "years": years,
        "baseline": base.__dict__,
        "assumptions": p,
        "series": series,
        "summary": {
            "disputes_avoided": base.pending_disputes - final["disputes_pending"],
            "disputes_avoided_range": [
                base.pending_disputes - final["disputes_pending_high"],
                base.pending_disputes - final["disputes_pending_low"],
            ],
            "avg_parcel_ha_change_pct": round(
                100 * (final["avg_parcel_ha"] - base.avg_parcel_ha) / max(base.avg_parcel_ha, 1e-9), 1
            ),
            "total_cost_inr": final["cumulative_cost_inr"],
        },
        "caveat": (
            "Projection based on the stated assumptions. Calibrate elasticity and cost "
            "parameters against completed consolidation rounds before use in policy."
        ),
    }
