from datetime import datetime

from pydantic import BaseModel

from src.shared.models import TaskStatus


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    status: TaskStatus = TaskStatus.IN_PROGRESS
    fulfilled_date: datetime | None = None
