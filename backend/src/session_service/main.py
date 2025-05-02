from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.session_service.as_tasks import startup_event, shutdown_event
from src.session_service.router import session_router
from src.shared.logger_setup import setup_logger

logger = setup_logger(__name__)
@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    # Load the routine
    logger.warning("Starting Celery worker and beat in the background...")
    await startup_event(fastapi_app)
    yield
    # Clean up release the resources
    await shutdown_event(fastapi_app)
    logger.warning("Shutdown event triggered")

app = FastAPI(title="Session Service")
app.include_router(session_router)