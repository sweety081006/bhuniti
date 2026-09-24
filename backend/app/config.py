from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(ROOT / ".env"), env_file_encoding="utf-8", extra="ignore"
    )

    # infrastructure
    # Prototype default: file-based, zero services to install.
    # Production (see the deck): postgresql+psycopg2://... with PostGIS, and a Qdrant server.
    database_url: str = f"sqlite:///{ROOT / 'data' / 'bhuniti.db'}"
    qdrant_path: str = str(ROOT / "data" / "qdrant")  # embedded mode; blank = use qdrant_url
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "bhuniti_chunks"

    # models (all local, no API keys)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    embedding_model: str = "intfloat/multilingual-e5-small"
    embedding_dim: int = 384

    # external keys (optional for the core demo)
    maptiler_key: str = ""
    data_gov_in_api_key: str = ""
    bhashini_user_id: str = ""
    bhashini_api_key: str = ""

    # app
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_ttl_minutes: int = 60 * 12
    pilot_state: str = "Bihar"
    cors_origins: str = (
        "https://frontend-ruddy-seven-43.vercel.app,"
        "https://frontend-d17d1c17k-sweety081006.vercel.app,"
        "https://frontend-fl71790it-sweety081006.vercel.app,"
        "https://*.vercel.app,"
        "http://localhost:3000"
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
