from fastapi import APIRouter, Depends, HTTPException, status, FastAPI

from src.user_service.database import SessionLocal

app = FastAPI()

def get_db():
    db = SessionLocal
    try:
        yield db
    finally:
        db.close()

app.post("/register")