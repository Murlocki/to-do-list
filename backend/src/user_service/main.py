from fastapi import FastAPI

from src.shared.logger_setup import setup_logger
from src.user_service.router import user_router

logger = setup_logger(__name__)


app = FastAPI()
app.include_router(user_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}




