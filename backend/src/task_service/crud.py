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
            status=task_create.status,
            fulfilled_date=task_create.fulfilled_date,
        )
        db.add(task)
        logger.info(f"Created task {task.to_dict()}")
    await db.refresh(task)
    return task

async def get_tasks_by_user_id(db:AsyncSession, user_id:int):
    async with db.begin():
        tasks = await db.execute(select(Task).filter(Task.user_id == user_id).order_by(Task.id))
        tasks = tasks.scalars().all()
        logger.info(f"Get tasks {tasks}")
    return tasks

async def delete_task_by_id(db:AsyncSession, task_id:int):
    async with db.begin():
        task = await db.execute(select(Task).filter(Task.id == task_id))
        task = task.scalar_one_or_none()
        if not task:
            logger.warning(f"Task {task_id} not found.")
            return None
        logger.info(f"Deleted task {task.to_dict()}")
        await db.delete(task)
    return task

async def update_task_by_id(db:AsyncSession, task_id:int, task_create:TaskCreate):
    async with db.begin():
        task = await db.execute(select(Task).filter(Task.id == task_id))
        task = task.scalar_one_or_none()
        if not task:
            logger.warning(f"Task {task_id} not found.")
            return None
        logger.info(f"Found old task {task.to_dict()}")
        update_data = task_create.model_dump(exclude_unset=True)
        logger.info(f"Updating task {update_data}")
        for key, value in update_data.items():
            setattr(task, key, value)
        task.version = task.version + 1
    await db.refresh(task)
    return task

async def get_task_by_id(db:AsyncSession, task_id:int):
    async with db.begin():
        task = await db.execute(select(Task).filter(Task.id == task_id))
        task = task.scalar_one_or_none()
        if not task:
            logger.error(f"Task {task_id} not found.")
            return None
        logger.info(f"Found task {task.to_dict()}")
        return task