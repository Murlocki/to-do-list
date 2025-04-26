import os
import time
from datetime import datetime
from typing import Any, Dict

from fastapi import HTTPException, status, APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.user_service import logger_setup, crud, auth_functions
from src.user_service.auth_functions import validate_password, get_session_by_token, decode_token, \
    verify_and_refresh_access_token
from src.user_service.crud import delete_inactive_sessions
from src.user_service.database import SessionLocal
from src.user_service.redis_base import redis_client
from src.user_service.schemas import UserCreate, Token, AuthForm

user_router = APIRouter()
logger = logger_setup.setup_logger(__name__)
logger.info(f"""
Server start time (UTC): {datetime.utcnow()}
Server timestamp: {int(time.time())}
System timezone: {time.tzname}
Environment timezone: {os.environ.get('TZ', 'Not set')}
""")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@user_router.post("/user/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    if not validate_password(user.password):
        logger.warning("Password does not meet complexity requirements")
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password error")

    # Check if user with the same email or username already exists
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        logger.warning(f"User with email {user.email} already exists")
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        logger.warning(f"User with username {user.username} already exists")
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    # Create new user
    result = crud.create_user(db=db, user=user)
    logger.info(f"User {user.username} registered")
    return HTTPException(status_code=status.HTTP_201_CREATED, detail=result)


@user_router.post("/user/login", response_model=Token)
def login_user(auth_form: AuthForm, db: Session = Depends(get_db)) -> HTTPException:
    user = crud.authenticate_user(db=db, identifier=auth_form.identifier, password=auth_form.password)
    if not user:
        logger.warning("Invalid credentials")
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Create access tokens
    access_token = auth_functions.create_new_token(user.email)
    logger.info(f"User {user.username} logged in with access token {access_token}")
    logger.info(auth_form.remember_me)
    # Create refresh token if remember_me is set
    if auth_form.remember_me:
        refresh_token = auth_functions.create_new_token(user.email, is_refresh=True)
        session_data = crud.create_and_store_session(user.id, access_token, refresh_token,
                                                     device=auth_form.device, ip_address=auth_form.ip_address)
        logger.info(f"User logged in (rem mode): {user.email}")
        # TODO: Оставить в ответе только access_token и token_type, остальное удалить ибо не нужно клиенту
        return HTTPException(status_code=status.HTTP_200_OK,
                             detail={"access_token": access_token, "refresh_token": refresh_token,
                                     "token_type": "bearer",
                                     "session_id": session_data["session_id"]})
    else:
        session_data = crud.create_and_store_session(user.id, access_token, remember=False)
        logger.info(f"User logged in: {user.email}")
        return HTTPException(status_code=status.HTTP_200_OK,
                             detail={"access_token": access_token, "token_type": "bearer",
                                     "session_id": session_data["session_id"]})


bearer = HTTPBearer()


@user_router.post("/user/logout")
def logout_user(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    token = credentials.credentials
    session = get_session_by_token(token, token_type="access_token")
    if not session:
        logger.warning("Session not found")
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    session_id = session.get("session_id")
    if session["session_id"]:
        redis_client.delete(f"session:{session_id}")
        redis_client.srem(f"user:{session['user_id']}:sessions", session_id)
        logger.info(f"Session {session_id} has been deleted")
        return HTTPException(status_code=status.HTTP_200_OK, detail="Logout successful")
    logger.warning(f"No session found for token during logout")
    return HTTPException(status_code=400, detail="Unable to logout. Session not found.")


@user_router.get("/user/check_auth")
def check_auth(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """
    Check if user is authenticated
    :param credentials: Carryind token in header
    :param db: Database session
    :return: Token data
    """
    token = credentials.credentials

    # Get token payload
    payload = decode_token(token)
    logger.info(f"Token decoded successfully {payload}")
    if not payload or not payload["sub"]:
        logger.warning("Invalid token")
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "Invalid token",
                                                                            "token": None})

    # Get token user
    user = crud.get_user_by_email(db, email=payload["sub"])
    if not user:
        logger.warning("User not found")
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "User is not found",
                                                                            "token": None})

    # Delete inactive sessions
    deleted_sessions: list[str] = delete_inactive_sessions(user.id)
    logger.info("Deleted inactive sessions: %s", deleted_sessions)

    # Check token validity and refresh if needed
    return HTTPException(status_code=status.HTTP_200_OK, detail={"token": verify_and_refresh_access_token(token)})
