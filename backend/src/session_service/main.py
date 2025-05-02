import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.session_service.as_tasks import listen_expirations
from src.session_service.redis_base import redis_client
from src.session_service.router import session_router
from src.shared.logger_setup import setup_logger

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Запускаем фоновую задачу
    task = asyncio.create_task(listen_expirations())
    logger.info("Started session expiration listener")

    yield  # FastAPI работает здесь

    # Остановка задачи при завершении
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logger.info("Stopped session expiration listener")
    await redis_client.close()


app = FastAPI(title="Session Service",lifespan=lifespan)
app.include_router(session_router)