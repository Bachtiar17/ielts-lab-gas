"""Application configuration loaded from environment / .env."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "IELTS Lab API"
    database_url: str = f"sqlite:///{PROJECT_ROOT / 'data' / 'ielts_lab.db'}"
    gemini_api_key: str | None = None
    gemini_fast_model: str = "gemini-3.5-flash-lite"
    gemini_pro_model: str = "gemini-4-neon"
    gemini_tts_model: str = "gemini-3.8-flash-lite-tts"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    taxonomy_path: Path = PROJECT_ROOT / "data" / "spec" / "idp_academic_taxonomy.json"
    notes_dir: Path = PROJECT_ROOT / "data" / "notes"
    audio_dir: Path = PROJECT_ROOT / "data" / "audio"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def has_gemini_key(self) -> bool:
        return bool(self.gemini_api_key and self.gemini_api_key.strip())


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
