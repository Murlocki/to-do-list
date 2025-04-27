from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.user_service.as_tasks import startup_event, shutdown_event
from src.user_service.logger_setup import setup_logger
from src.user_service.router import user_router

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    # Load the routine
    await startup_event(fastapi_app)
    yield
    # Clean up release the resources
    await shutdown_event(fastapi_app)
    logger.warning("Shutdown event triggered")

app = FastAPI(lifespan=lifespan)
app.include_router(user_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}



