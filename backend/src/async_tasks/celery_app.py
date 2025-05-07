from datetime import timedelta

from celery import Celery

from src.shared.config import settings

app = Celery(
    'async_tasks',
    broker=f'redis://:{settings.redis_password}@{settings.redis_host}:{settings.redis_port}/{settings.redis_db}',
    include=['src.async_tasks.tasks'],  # Критически важно!
    backend=f'redis://:{settings.redis_password}@{settings.redis_host}:{settings.redis_port}/{settings.redis_db}'
)

app.conf.update(
    pool="solo",
    task_serializer='json',
    result_serializer='json',
    timezone='UTC',
    beat_schedule={
        'process-tasks': {
            'task': 'src.async_tasks.tasks.dispatch_chunks',  # Указываем задачу-диспетчер
            'schedule': timedelta(hours=settings.task_remind_timer_hours, minutes=settings.task_remind_timer_minutes,
                                  seconds=settings.task_remind_timer_seconds),
            'args': (),  # Пустые аргументы, так как dispatch_chunks не принимает параметров
        },
    }
)
