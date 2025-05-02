from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.task_service.router import task_router
from src.shared.logger_setup import setup_logger

logger = setup_logger(__name__)

app = FastAPI(title="Task Service")
app.include_router(task_router)