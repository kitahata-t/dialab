from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    """Application configuration values."""

    openai_api_key: str
    database_path: Path
    openai_model: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load configuration from environment variables and cache the result."""
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Provide it via environment variables or .env.")

    db_path = Path(os.getenv("DATABASE_PATH", "data/app.db"))
    db_path.parent.mkdir(parents=True, exist_ok=True)

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    return Settings(openai_api_key=api_key, database_path=db_path, openai_model=model)
