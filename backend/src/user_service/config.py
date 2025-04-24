import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(verbose=True)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    postgres_user: str = ""
    postgres_password: str = ""
    postgres_db: str = ""
    redis_host: str = ""
    redis_port: int = 6379
    redis_password: str = ""
    redis_db: str = ""
    log_dir: str = os.path.join(BASE_DIR, "logs")
    log_file: str = os.path.join(log_dir, "app.log")


settings = Settings()
