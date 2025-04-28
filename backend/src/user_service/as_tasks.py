import asyncio
import subprocess
import os
import signal
from contextlib import contextmanager

from datetime import timedelta
from celery import Celery
from fastapi import FastAPI

from src.user_service import crud
from src.user_service.config import settings
from src.user_service.crud import delete_inactive_sessions
from src.user_service.logger_setup import setup_logger

celery_app = Celery(
    'user_service_tasks',
    broker=f'redis://:{settings.redis_password}@{settings.redis_host}:{settings.redis_port}/{settings.redis_db}'
)

# Конфигурация для Windows
celery_app.conf.update(
    task_pool="solo",
    worker_max_tasks_per_child=100,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True
)

logger = setup_logger(__name__)

@celery_app.task
def cleanup_inactive_sessions():
    """Фоновая задача очистки сессий"""
    try:
            # Todo: Получить всех пользователей из базы данных
            users = asyncio.run(crud.get_all_users())
            for user in users:
                delete_inactive_sessions(user.id)
            logger.info("Inactive sessions cleaned up")
    except Exception as e:
        logger.error(f"Cleanup error: {e}")


celery_app.conf.beat_schedule = {
    'cleanup_sessions_hourly': {
        'task': 'src.session_service.as_tasks.cleanup_inactive_sessions',
        'schedule': timedelta(seconds = settings.session_cleanup_seconds,
                              minutes=settings.session_cleanup_minutes,
                             hours=settings.session_cleanup_hours,
                              days = settings.session_cleanup_days)
    },
}


def run_worker():
    """Запуск worker для Windows без открытия консоли"""
    # Создаем файлы для логов
    with open('celery_worker.log', 'w') as f:
        pass
    with open('celery_worker_err.log', 'w') as f:
        pass

    # Запуск worker в фоновом режиме
    worker_process = subprocess.Popen(
        [
            'celery', '-A', 'src.session_service.as_tasks',
            'worker', '--pool=solo', '--loglevel=INFO'
        ],
        stdout=open('celery_worker.log', 'w'),
        stderr=open('celery_worker_err.log', 'w'),
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )
    return worker_process


def run_beat():
    """Запуск beat для Windows без открытия консоли"""
    # Создаем файлы для логов
    with open('celery_beat.log', 'w') as f:
        pass
    with open('celery_beat_err.log', 'w') as f:
        pass

    # Запуск beat в фоновом режиме
    beat_process = subprocess.Popen(
        [
            'celery', '-A', 'src.session_service.as_tasks',
            'beat', '--loglevel=INFO'
        ],
        stdout=open('celery_beat.log', 'w'),
        stderr=open('celery_beat_err.log', 'w'),
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )
    return beat_process


async def startup_event(app: FastAPI):
    """Запуск при старте приложения"""
    logger.info("Starting Celery worker and beat in the background...")

    # Запускаем worker и beat
    worker_process = run_worker()
    beat_process = run_beat()

    # Сохраняем процессы в состоянии приложения
    app.state.celery_worker = worker_process
    app.state.celery_beat = beat_process

    logger.info(f"Celery worker PID: {worker_process.pid}")
    logger.info(f"Celery beat PID: {beat_process.pid}")


async def shutdown_event(app: FastAPI):
    """Завершение процессов при остановке приложения"""
    logger.info("Shutting down Celery worker and beat...")

    # Завершаем worker
    if hasattr(app.state, 'celery_worker'):
        worker = app.state.celery_worker
        try:
            worker.send_signal(signal.CTRL_BREAK_EVENT if os.name == 'nt' else signal.SIGTERM)
            worker.wait(timeout=10)
            logger.info("Celery worker terminated successfully")
        except subprocess.TimeoutExpired:
            logger.warning("Celery worker did not terminate gracefully, killing...")
            worker.kill()
        except Exception as e:
            logger.error(f"Error stopping Celery worker: {e}")

    # Завершаем beat
    if hasattr(app.state, 'celery_beat'):
        beat = app.state.celery_beat
        try:
            # Для Windows используем CTRL_BREAK_EVENT
            beat.send_signal(signal.CTRL_BREAK_EVENT if os.name == 'nt' else signal.SIGTERM)
            beat.wait(timeout=10)
            logger.info("Celery beat terminated successfully")
        except subprocess.TimeoutExpired:
            logger.warning("Celery beat did not terminate gracefully, killing...")
            beat.kill()
        except Exception as e:
            logger.error(f"Error stopping Celery beat: {e}")

    logger.info("Shutdown complete")