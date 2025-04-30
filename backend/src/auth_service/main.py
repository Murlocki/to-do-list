from fastapi import FastAPI
from src.shared.logger_setup import setup_logger
from src.auth_service.router import auth_router

logger = setup_logger(__name__)


app = FastAPI()
app.include_router(auth_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}




