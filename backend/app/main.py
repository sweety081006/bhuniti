from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import init_db
from .routers import auth, dashboard, documents, gis, search, simulation

app = FastAPI(
    title="BhuNiti API",
    description=(
        "National Digital Platform for Research, Policy Innovation and "
        "Evidence-Based Land Governance - SIH 2026, PS 26019 (MoRD / DoLR)."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(search.router)
app.include_router(gis.router)
app.include_router(simulation.router)
app.include_router(dashboard.router)


@app.on_event("startup")
def _startup() -> None:
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok", "pilot_state": settings.pilot_state}
