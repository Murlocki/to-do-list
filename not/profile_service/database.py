from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from src.profile_service.config import settings


# Создаем движок для подключения к базе данных PostgreSQL
engine = create_engine(settings.postgres_db, echo=True)

# Создаем фабрику сессий для работы с базой данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем базовый класс для моделей
Base = declarative_base()

def check_database_connection():
    try:
        response = engine.connect()
        return response
    except:
        return False
if __name__ == '__main__':
    print(check_database_connection())

