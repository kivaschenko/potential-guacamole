from pydantic_settings import BaseSettings
from typing import Optional, Any
from pathlib import Path

# TODO: remove this and excchange with import dotenv in root __init__.py
class Settings(BaseSettings):
    pguser: str
    pgpassword: str
    pgdatabase: str
    pgport: int
    pghost: str
    jwt_secret: str
    jwt_expires_in: int = 60 * 24  # 1 day
    app_name: str = "Authentiaon API | Graintrade Platform"
    DATABASE_URL: Optional[str] = None
    BASE_DIR: Path = (
        Path(__file__).resolve().parent
    )  # Path to the directory where the settings file is located
    dev_mode: bool = True

    def model_post_init(self, __context: Any) -> None:
        """Override this method to perform additional initialization after `__init__`
        and `model_construct`. This is useful if you want to do some validation that
        requires the entire model to be initialized.
        """
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"postgresql://{self.pguser}:{self.pgpassword}@{self.pghost}:{self.pgport}/{self.pgdatabase}"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
