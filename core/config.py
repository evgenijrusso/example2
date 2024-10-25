from pathlib import Path
import logging
from pydantic_settings import BaseSettings

logging.basicConfig(level=logging.INFO)

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """App settings."""

    project_name: str = "example2"
    db_echo: bool = True  # пока True, потом False

    db_url: str = f"sqlite+aiosqlite:///{BASE_DIR}/db_example2.sqlite3"


settings = Settings()
