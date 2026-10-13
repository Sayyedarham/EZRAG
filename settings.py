"""Runtime configuration for the hosted RAG Workbench."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _int_env(name: str, default: int, *, minimum: int = 1) -> int:
    value = os.getenv(name, str(default))
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer.") from exc
    if parsed < minimum:
        raise ValueError(f"{name} must be at least {minimum}.")
    return parsed


def _bool_env(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().casefold() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_environment: str
    openai_api_key: str
    chat_model: str
    embedding_model: str
    allow_user_api_keys: bool
    max_upload_bytes: int
    max_upload_files: int
    max_pdf_pages: int
    max_chunks: int
    max_queries_per_minute: int

    @property
    def is_production(self) -> bool:
        return self.app_environment == "production"


def load_settings() -> Settings:
    """Read and validate environment-based configuration once per process."""
    environment = os.getenv("APP_ENV", "development").strip().casefold()
    if environment not in {"development", "staging", "production"}:
        raise ValueError("APP_ENV must be development, staging, or production.")
    allow_user_keys = _bool_env("ALLOW_USER_API_KEYS", default=environment == "development")
    return Settings(
        app_environment=environment,
        openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        chat_model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini").strip(),
        embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small").strip(),
        allow_user_api_keys=allow_user_keys,
        max_upload_bytes=_int_env("MAX_UPLOAD_MB", 10) * 1024 * 1024,
        max_upload_files=_int_env("MAX_UPLOAD_FILES", 10),
        max_pdf_pages=_int_env("MAX_PDF_PAGES", 100),
        max_chunks=_int_env("MAX_CHUNKS_PER_SESSION", 2_000),
        max_queries_per_minute=_int_env("MAX_QUERIES_PER_MINUTE", 20),
    )
