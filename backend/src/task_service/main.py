import asyncio
from contextlib import asynccontextmanager

from src.shared.logger_setup import setup_logger
from src.task_service.router import task_router

logger = setup_logger(__name__)

# Создаем FastAPI

from fastapi import FastAPI
from socketio import ASGIApp, AsyncServer


def socketio_mount(
    app: FastAPI,
    async_mode: str = "asgi",
    mount_path: str = "/socket.io/",
    socketio_path: str = "socket.io",
    cors_allowed_origins="*",
    **kwargs
) -> AsyncServer:
    """Mounts an async SocketIO app over an FastAPI app."""

    sio = AsyncServer(async_mode=async_mode,
                      cors_allowed_origins=cors_allowed_origins,
                      logger=logger,
                      engineio_logger=logger, **kwargs)

    sio_app = ASGIApp(sio, socketio_path=socketio_path)

    # mount
    app.add_route(mount_path, route=sio_app, methods=["GET", "POST"])
    app.add_websocket_route(mount_path, sio_app)

    return sio


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запускаем консьюмер при старте
    logger.info("Kafka started")
    consumer_task = asyncio.create_task(consume_kafka_messages())

    yield  # Здесь работает приложение

    # Останавливаем при завершении
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        logger.info("Kafka consumer stopped gracefully")

fastapi_app = FastAPI(title="Task Service", lifespan=lifespan)
fastapi_app.include_router(task_router)

sio = socketio_mount(fastapi_app)

from src.task_service.websocket_router import *
from src.task_service.kafka_consumer import consume_kafka_messages