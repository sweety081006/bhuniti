"""Seed the database with demo users, the starter corpus, synthetic Bihar parcels
and illustrative district statistics.

Run from the repo root with the venv active:
    python -m backend.seed.seed            # seed everything
    python -m backend.seed.seed --reset    # wipe first, then seed
"""

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.app.db import SessionLocal, engine, init_db  # noqa: E402
from backend.app.models import (  # noqa: E402
    DisputeStat,
    Document,
    Indicator,
    Parcel,
    User,
)
from backend.app.security import hash_password  # noqa: E402
from backend.app.services import ingest  # noqa: E402
from backend.seed.corpus import CORPUS  # noqa: E402

random.seed(26019)  # reproducible demo data

# Pilot geography: Bihar. Centroids are approximate district headquarters.
DISTRICTS = [
    # name,        lat,     lon,     flood-prone (north Bihar / Kosi belt)
    ("Patna", 25.594, 85.137, False),
    ("Muzaffarpur", 26.122, 85.391, True),
    ("Gaya", 24.796, 85.000, False),
    ("Purnia", 25.777, 87.475, True),
]

BLOCKS = ["Sadar", "Paroo", "Bihta", "Barh", "Dhamdaha", "Manpur"]
VILLAGES = ["Rampur", "Madhopur", "Bishunpur", "Chakia", "Sonbarsa", "Harpur", "Jagdishpur"]
LAND_USE = ["agriculture", "agriculture", "agriculture", "builtup", "fallow", "water", "forest"]


def demo_users() -> list[dict]:
    return [
        {"email": "researcher@bhuniti.in", "name": "Dr. A. Researcher", "role": "researcher",
         "organisation": "Centre for Land Studies", "password": "demo1234"},
        {"email": "legal@bhuniti.in", "name": "Adv. C. Verma", "role": "legal",
         "organisation": "Bihar Land Tribunal", "password": "demo1234"},
        {"email": "official@bhuniti.in", "name": "Shri B. Kumar (DoLR)", "role": "official",
         "organisation": "Dept of Land Resources, MoRD", "password": "demo1234"},
        {"email": "institution@bhuniti.in", "name": "State Survey Directorate", "role": "institution",
         "organisation": "DLRS, Govt of Bihar", "password": "demo1234"},
    ]


def seed_users(db) -> None:
    for u in demo_users():
        if db.query(User).filter(User.email == u["email"]).first():
            continue
        db.add(
            User(
                email=u["email"], name=u["name"], role=u["role"],
                organisation=u["organisation"], password_hash=hash_password(u["password"]),
            )
        )
    db.commit()
    print(f"users:      {db.query(User).count()}")


def seed_documents(db, index: bool = True) -> None:
    created = 0
    for item in CORPUS:
        if db.query(Document).filter(Document.title == item["title"]).first():
            continue
        doc = Document(**item)
        db.add(doc)
        db.commit()
        db.refresh(doc)
        created += 1
        if index:
            n = ingest.index_document(db, doc)
            print(f"  indexed {n:>3} chunks - {doc.title[:64]}")
    print(f"documents:  {db.query(Document).count()} (new: {created})")


def _square(lat: float, lon: float, side_deg: float) -> str:
    """A square parcel as a GeoJSON Polygon string (EPSG:4326)."""
    h = side_deg / 2
    ring = [
        [lon - h, lat - h], [lon + h, lat - h], [lon + h, lat + h],
        [lon - h, lat + h], [lon - h, lat - h],
    ]
    return json.dumps({"type": "Polygon", "coordinates": [ring]})


def seed_parcels(db, per_district: int = 160) -> None:
    if db.query(Parcel).count() > 0:
        print(f"parcels:    {db.query(Parcel).count()} (already present, skipped)")
        return

    for d_i, (district, lat0, lon0, flood) in enumerate(DISTRICTS):
        for i in range(per_district):
            lat = lat0 + random.uniform(-0.14, 0.14)
            lon = lon0 + random.uniform(-0.14, 0.14)
            # small holdings dominate; a few larger ones
            side = random.choice([0.0004, 0.0005, 0.0007, 0.0009, 0.0012, 0.0018])  # ~0.2-4 ha
            geom_json = _square(lat, lon, side)
            # ~1 deg lat == 111 km; area in hectares
            area_ha = round((side * 111_000) ** 2 / 10_000, 3)

            land_use = random.choice(LAND_USE)
            owners = random.choices([1, 2, 3, 4, 6], weights=[45, 25, 15, 10, 5])[0]
            dispute = random.choices(
                ["none", "pending", "resolved"],
                weights=[72, 18, 10] if not flood else [66, 23, 11],
            )[0]
            risk = (
                random.choices(["low", "medium", "high"], weights=[20, 35, 45])[0]
                if flood
                else random.choices(["low", "medium", "high"], weights=[60, 30, 10])[0]
            )

            db.add(
                Parcel(
                    parcel_uid=f"BR{d_i+1:02d}{i+1:05d}",
                    state="Bihar", district=district,
                    block=random.choice(BLOCKS), village=random.choice(VILLAGES),
                    land_use=land_use, area_ha=area_ha, owners=owners,
                    dispute_status=dispute, climate_risk=risk, source="synthetic",
                    geom_json=geom_json,
                )
            )
        db.commit()
    print(f"parcels:    {db.query(Parcel).count()} (synthetic)")


def seed_stats(db) -> None:
    if db.query(DisputeStat).count() == 0:
        for district, *_ in DISTRICTS:
            pending = random.randint(2800, 9200)
            for year in (2022, 2023, 2024, 2025):
                disposed = int(pending * random.uniform(0.18, 0.30))
                db.add(
                    DisputeStat(
                        state="Bihar", district=district, year=year,
                        pending_cases=pending, disposed_cases=disposed,
                        avg_pendency_days=random.randint(900, 2100), source="synthetic",
                    )
                )
                pending = int(pending * random.uniform(0.97, 1.06))
        db.commit()
    print(f"disputes:   {db.query(DisputeStat).count()} rows (synthetic)")

    if db.query(Indicator).count() == 0:
        for district, *_ in DISTRICTS:
            for year in (2022, 2023, 2024, 2025):
                db.add(Indicator(name="RoR digitisation", state="Bihar", district=district,
                                 year=year, value=round(random.uniform(78, 97), 1), unit="%",
                                 source="synthetic"))
                db.add(Indicator(name="Map-record linkage", state="Bihar", district=district,
                                 year=year, value=round(random.uniform(35, 78), 1), unit="%",
                                 source="synthetic"))
                db.add(Indicator(name="Mutation turnaround", state="Bihar", district=district,
                                 year=year, value=round(random.uniform(21, 95), 1), unit="days",
                                 source="synthetic"))
        db.commit()
    print(f"indicators: {db.query(Indicator).count()} rows (synthetic)")


def reset(db) -> None:
    from backend.app.services import vectorstore

    for model in (Indicator, DisputeStat, Parcel, Document, User):
        db.query(model).delete()
    db.commit()
    try:
        vectorstore.client().delete_collection(
            collection_name=vectorstore.settings.qdrant_collection
        )
    except Exception:
        pass
    print("reset:      all tables cleared, vector collection dropped")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reset", action="store_true", help="wipe existing data first")
    ap.add_argument("--no-index", action="store_true", help="skip embedding (faster, no AI search)")
    args = ap.parse_args()

    init_db()
    db = SessionLocal()
    try:
        if args.reset:
            reset(db)
        print(f"database:   {engine.url.render_as_string(hide_password=True)}")
        seed_users(db)
        seed_parcels(db)
        seed_stats(db)
        seed_documents(db, index=not args.no_index)
    finally:
        db.close()

    print("\nDone. Demo logins (password: demo1234)")
    for u in demo_users():
        print(f"  {u['role']:<12} {u['email']}")


if __name__ == "__main__":
    main()
