from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(verbose=True)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    postgres_user: str = ""
    postgres_password: str = ""
    postgres_db: str = ""
settings = Settings()
print(settings.postgres_db)
print(settings.postgres_user)
print(settings.postgres_password)

