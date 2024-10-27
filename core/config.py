from pathlib import Path
import logging
from pydantic_settings import BaseSettings

logging.basicConfig(level=logging.INFO)

BASE_DIR = Path(__file__).resolve().parent.parent
print("BASE_DIR:", BASE_DIR)


class Settings(BaseSettings):
    """App settings."""

    project_name: str = "example2"
    db_echo: bool = True  # пока True, потом False
    api_v1_prefix: str = "/api/v1"

    db_url: str = f"sqlite+aiosqlite:///{BASE_DIR}/db_example2.sqlite3"


settings = Settings()
print("DB URL =>", settings.db_url)
