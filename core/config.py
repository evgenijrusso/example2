from pathlib import Path
from pydantic import BaseModel
import logging
from pydantic_settings import BaseSettings

logging.basicConfig(level=logging.INFO)

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db_example2.sqlite3"
# print("BASE_DIR:", BASE_DIR)


class DbSettings(BaseModel):
    # url: str = f"sqlite+aiosqlite:///{BASE_DIR}/db_example2.sqlite3"
    url: str = f"sqlite+aiosqlite:///{DB_PATH}"
    echo: bool = True  # пока True, потом False


class Settings(BaseSettings):
    """App settings."""

    project_name: str = "example2"
    api_v1_prefix: str = "/api/v1"
    db: DbSettings = DbSettings()  # вложенный объект


settings = Settings()
print("DB URL =>", settings.db.url)
