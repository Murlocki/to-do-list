from datetime import datetime

from pydantic import BaseModel, AliasChoices, Field

from src.shared.models import TaskStatus


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    status: TaskStatus = TaskStatus.IN_PROGRESS
    fulfilled_date: datetime | None = Field(None,validation_alias=AliasChoices('fulfilled_date', 'fulfilledDate'))
    version: int | None = None
