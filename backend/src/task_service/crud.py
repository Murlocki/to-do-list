# CRUD сессией
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.logger_setup import setup_logger
from src.shared.models import Task
from src.task_service.schemas import TaskCreate

logger = setup_logger(__name__)

async def create_task(task_create: TaskCreate, user_id:int,  db:AsyncSession):
    async with db.begin():
        task = Task(
            user_id=user_id,
            title=task_create.title,
            description=task_create.description,
            fulfilled_date=task_create.fulfilled_date,
        )
        db.add(task)
        logger.info(f"Created task {task.to_dict()}")
    await db.refresh(task)
    return task

async def get_tasks_by_user_id(db:AsyncSession, user_id:int):
    async with db.begin():
        tasks = await db.execute(select(Task).filter(Task.user_id == user_id))
        tasks = tasks.scalars().all()
        logger.info(f"Get tasks {tasks}")
    return tasks