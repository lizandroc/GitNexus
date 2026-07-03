"""Central configuration for the local AI platform.

Everything is environment-driven with safe local-first defaults:
no cloud calls are possible unless LAP_ALLOW_CLOUD=true is set explicitly.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _env_bool(name: str, default: bool) -> bool:
    val = os.environ.get(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


@dataclass
class Settings:
    # Where documents, the SQLite DB, and logs live. Local disk only.
    data_dir: Path = field(
        default_factory=lambda: Path(os.environ.get("LAP_DATA_DIR", "./data")).resolve()
    )
    host: str = os.environ.get("LAP_HOST", "127.0.0.1")
    port: int = int(os.environ.get("LAP_PORT", "8130"))

    # Provider endpoints (both are localhost runtimes on the Mac).
    ollama_url: str = os.environ.get("LAP_OLLAMA_URL", "http://127.0.0.1:11434")
    lmstudio_url: str = os.environ.get("LAP_LMSTUDIO_URL", "http://127.0.0.1:1234")

    # Default provider/model used until the user picks one in the dashboard.
    default_provider: str = os.environ.get("LAP_PROVIDER", "ollama")
    default_model: str = os.environ.get("LAP_MODEL", "llama3.2:3b")
    embedding_model: str = os.environ.get("LAP_EMBEDDING_MODEL", "nomic-embed-text")

    # Auto-routing tiers: the small model most requests land on, and the
    # larger model reserved for reasoning-heavy or long-input tasks.
    fast_model: str = os.environ.get("LAP_MODEL_FAST", "llama3.2:3b")
    quality_model: str = os.environ.get("LAP_MODEL_QUALITY", "qwen2.5:7b")

    # Privacy: local_only blocks every non-localhost provider. Cloud mode must
    # be enabled explicitly by the user — never by code.
    allow_cloud: bool = field(default_factory=lambda: _env_bool("LAP_ALLOW_CLOUD", False))

    # Optional bearer token for the API. Empty string disables auth (MVP,
    # localhost-only). Set LAP_API_KEY for anything beyond a single-user Mac.
    api_key: str = os.environ.get("LAP_API_KEY", "")

    # RAG parameters.
    chunk_size: int = int(os.environ.get("LAP_CHUNK_SIZE", "1200"))
    chunk_overlap: int = int(os.environ.get("LAP_CHUNK_OVERLAP", "200"))
    top_k: int = int(os.environ.get("LAP_TOP_K", "5"))

    request_timeout: float = float(os.environ.get("LAP_TIMEOUT", "300"))

    @property
    def db_path(self) -> Path:
        return self.data_dir / "platform.db"

    @property
    def docs_dir(self) -> Path:
        return self.data_dir / "documents"

    def ensure_dirs(self) -> None:
        self.docs_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
