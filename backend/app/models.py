from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base

# Roles used across the platform (PS point 17: secure role-based access)
ROLES = ("researcher", "legal", "official", "institution", "public")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(30), default="public")
    organisation: Mapped[str] = mapped_column(String(200), default="")
    password_hash: Mapped[str] = mapped_column(String(255))


class Document(Base):
    """A repository item: research paper, policy document, act, judgment, dataset note."""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(500), index=True)
    doc_type: Mapped[str] = mapped_column(String(50), index=True)  # policy|research|legal|dataset|case_study
    publisher: Mapped[str] = mapped_column(String(300), default="")
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    state: Mapped[str] = mapped_column(String(100), default="India", index=True)
    url: Mapped[str] = mapped_column(String(1000), default="")
    # provenance: "official" | "peer_reviewed" | "synthetic" - drives the Evidence Score
    provenance: Mapped[str] = mapped_column(String(30), default="official", index=True)
    body: Mapped[str] = mapped_column(Text, default="")
    n_chunks: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Parcel(Base):
    """Cadastral parcel. In the MVP these are synthetic stand-ins for RoR/Bhunaksha data."""

    __tablename__ = "parcels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    parcel_uid: Mapped[str] = mapped_column(String(60), unique=True, index=True)  # ULPIN-style id
    state: Mapped[str] = mapped_column(String(100), index=True)
    district: Mapped[str] = mapped_column(String(100), index=True)
    block: Mapped[str] = mapped_column(String(100), default="")
    village: Mapped[str] = mapped_column(String(100), default="")
    land_use: Mapped[str] = mapped_column(String(50), index=True)  # agriculture|builtup|fallow|water|forest
    area_ha: Mapped[float] = mapped_column(Float, default=0.0)
    owners: Mapped[int] = mapped_column(Integer, default=1)  # fragmentation proxy
    dispute_status: Mapped[str] = mapped_column(String(30), default="none", index=True)  # none|pending|resolved
    climate_risk: Mapped[str] = mapped_column(String(20), default="low")  # low|medium|high (flood proneness)
    source: Mapped[str] = mapped_column(String(30), default="synthetic")
    # GeoJSON geometry as text (EPSG:4326). On Postgres this becomes a PostGIS
    # geometry column; SQLite keeps it as text so the prototype needs no services.
    geom_json: Mapped[str] = mapped_column(Text)


class DisputeStat(Base):
    """District-level land dispute counts (NJDG-style) used by the dashboard."""

    __tablename__ = "dispute_stats"
    __table_args__ = (UniqueConstraint("district", "year", name="uq_dispute_district_year"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    state: Mapped[str] = mapped_column(String(100), index=True)
    district: Mapped[str] = mapped_column(String(100), index=True)
    year: Mapped[int] = mapped_column(Integer, index=True)
    pending_cases: Mapped[int] = mapped_column(Integer, default=0)
    disposed_cases: Mapped[int] = mapped_column(Integer, default=0)
    avg_pendency_days: Mapped[int] = mapped_column(Integer, default=0)
    source: Mapped[str] = mapped_column(String(30), default="synthetic")


class Indicator(Base):
    """Generic policy performance indicator (PS point 16)."""

    __tablename__ = "indicators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    state: Mapped[str] = mapped_column(String(100), default="Bihar", index=True)
    district: Mapped[str] = mapped_column(String(100), default="", index=True)
    year: Mapped[int] = mapped_column(Integer, index=True)
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(50), default="")
    source: Mapped[str] = mapped_column(String(30), default="synthetic")


class Workspace(Base):
    """Collaborative workspace (PS point 9) - minimal version for the MVP."""

    __tablename__ = "workspaces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
