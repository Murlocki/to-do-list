from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(verbose=True)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    postgres_user: str = ""
    postgres_password: str = ""
    postgres_db: str = ""
    redis_host: str = ""
    redis_port: int = 6379
    redis_password: str = ""
    redis_db: str = ""
settings = Settings()


