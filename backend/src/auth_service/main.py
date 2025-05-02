from fastapi import FastAPI

from src.auth_service.router import auth_router
from src.shared.logger_setup import setup_logger

logger = setup_logger(__name__)


app = FastAPI()
app.include_router(auth_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}




