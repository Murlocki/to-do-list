import asyncio
import datetime
from functools import partial

from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker

from src.async_tasks.kafka_producer import send_to_kafka
from src.shared.config import settings
from src.shared.logger_setup import setup_logger

logger = setup_logger(__name__)


# Создаем синхронную сессию
# TODO: Добавить нормальный путь на синхронный движок ну или так оставить
engine = create_engine(settings.postgres_db.replace("+asyncpg","+psycopg2"), echo=True)
SyncSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

from src.shared.models import User, Task, TaskStatus

from sqlalchemy import select, func, and_


def sync_send_to_kafka(message):
    """Синхронная обертка для асинхронной отправки в Kafka"""
    try:
        # Создаем новый event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Создаем частично примененную функцию для запуска
        send_func = partial(
            send_to_kafka,
            message=message
        )

        # Запускаем корутину
        loop.run_until_complete(send_func())
        logger.info("Successfully sent to Kafka for user %s", message.get("user"))
    except Exception as e:
        logger.error("Failed to send to Kafka: %s", str(e))
    finally:
        # Всегда закрываем loop
        loop.close()
        asyncio.set_event_loop(None)

def process_users_chunk(chunk_index):
    """Синхронная обработка чанка"""
    with SyncSessionLocal() as session:
        try:
            # Получаем общее количество пользователей
            total_users = session.scalar(select(func.count()).select_from(User))
            logger.info("Total users: %s", total_users)
            if not total_users:
                logger.info("No users found.")
                return

            # Расчет смещения и лимита
            user_per_chunk = max(1, total_users // 4)  # Жестко 4 чанка
            offset = chunk_index * user_per_chunk
            logger.info("Processing chunk %s with offset %s", chunk_index, offset)
            # Получаем пользователей чанка
            users = session.scalars(
                select(User).offset(offset).limit(user_per_chunk)
            ).all()
            logger.info("Users: %s", users)
            for user in users:
                # Обработка задач пользователя
                tasks = session.scalars(
                    select(Task).where(
                        and_(
                            Task.user_id == user.id,
                            Task.status == TaskStatus.IN_PROGRESS,
                            or_
                            (Task.fulfilled_date < datetime.datetime.now(),
                             Task.fulfilled_date == None)
                        )
                    )
                ).all()
                logger.info("Tasks for user %s: %s", user.id, tasks)
                if tasks:
                    message = {
                        "event": "task_due",
                        "user": user.id,
                        "tasks": [task.to_dict() for task in tasks]
                    }
                    sync_send_to_kafka(message)
                    logger.info("Sent tasks to Kafka for user %s", user.id)
            return f"Processed chunk {chunk_index} with {len(users)} users"

        except Exception as e:
            logger.error(f"Error in chunk {chunk_index}: {str(e)}")
            raise