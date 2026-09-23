from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings

IS_SQLITE = settings.database_url.startswith("sqlite")
if IS_SQLITE:
    Path(settings.database_url.replace("sqlite:///", "")).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    future=True,
    connect_args={"check_same_thread": False} if IS_SQLITE else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create tables (and PostGIS when running on Postgres). Safe on every boot."""
    from . import models  # noqa: F401  (registers the mappers)

    if not IS_SQLITE:
        with engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
    Base.metadata.create_all(engine)
