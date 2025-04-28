import os
import time
from datetime import datetime

from fastapi import HTTPException, status, APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from src.profile_service import auth_functions, crud
from src.shared import logger_setup
from src.user_service import validate_password, get_session_by_token, decode_token, \
    verify_and_refresh_access_token, get_password_hash
from src.user_service import delete_inactive_sessions
from src.user_service import SessionLocal
from src.profile_service.redis_base import redis_client
from src.profile_service.schemas import UserCreate, AuthForm, TokenModelResponse, UserResponse, SessionDTO, UserUpdate

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

bearer = HTTPBearer()

@user_router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    if not validate_password(user.password):
        logger.warning("Password does not meet complexity requirements")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password error")

    # Check if user with the same email or username already exists
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        logger.warning(f"User with email {user.email} already exists")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        logger.warning(f"User with username {user.username} already exists")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    # Create new user
    result = crud.create_user(db=db, user=user)
    logger.info(f"User {user.username} registered")
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result.to_dict())


@user_router.post("/auth/login", response_model=TokenModelResponse, status_code=status.HTTP_200_OK)
def login_user(auth_form: AuthForm, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db=db, identifier=auth_form.identifier, password=auth_form.password)
    if not user:
        logger.warning("Invalid credentials")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

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
        return JSONResponse(status_code=status.HTTP_200_OK,
                             content={"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token,
                                      "session_id": session_data["session_id"]})
    else:
        session_data = crud.create_and_store_session(user.id, access_token)
        logger.info(f"User logged in: {user.email}")
        return JSONResponse(status_code=status.HTTP_200_OK,
                             content={"access_token": access_token, "token_type": "bearer",
                                      "session_id": session_data["session_id"]})

@user_router.post("/auth/logout", status_code=status.HTTP_200_OK)
def logout_user(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    token = credentials.credentials
    session = get_session_by_token(token, token_type="access_token")
    if not session:
        logger.warning("Session not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    session_id = session.get("session_id")
    if session["session_id"]:
        redis_client.delete(f"session:{session_id}")
        redis_client.srem(f"user:{session['user_id']}:sessions", session_id)
        logger.info(f"Session {session_id} has been deleted")
        return JSONResponse(status_code=status.HTTP_200_OK, content="Logout successful")
    logger.warning(f"No session found for token during logout")
    raise HTTPException(status_code=400, detail="Unable to logout. Session not found.")

@user_router.get("/auth/me/check_auth", response_model=TokenModelResponse)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "Invalid token",
                                                                            "token": None})

    # Get token user
    user = crud.get_user_by_email(db, email=payload["sub"])
    logger.info(f"{user.to_dict()}, {payload['sub']}")
    if not user:
        logger.warning("User not found 214")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "User is not found",
                                                                            "token": None})

    # Delete inactive sessions
    deleted_sessions: list[str] = delete_inactive_sessions(user.id)
    logger.info("Deleted inactive sessions: %s", deleted_sessions)

    # Check token validity and refresh if needed
    return JSONResponse(status_code=status.HTTP_200_OK, content={"access_token": verify_and_refresh_access_token(token)})

@user_router.delete("/auth/me/account", status_code=status.HTTP_200_OK)
def delete_me(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """
    Delete of my self
    :param credentials: Headers with token
    :param db: Database session
    :return: None
    """
    verify_result = check_auth(credentials, db)
    if verify_result.status_code == status.HTTP_200_OK:
        token = decode_token(credentials.credentials)
        user = crud.get_user_by_email(db, email=token["sub"])
        if not user:
            logger.warning("User not found 141")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        logger.info(f"User {user.username} deleted")
        return JSONResponse(status_code=status.HTTP_200_OK, content="User deleted")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@user_router.patch("/auth/me/password", status_code=status.HTTP_200_OK)
def update_password(password:str, credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """
    Update user password
    :param password: New password
    :param credentials: Headers with token
    :param db: Database session
    :return: None
    """
    verify_result = check_auth(credentials, db)
    if verify_result.status_code == status.HTTP_200_OK:
        payload = decode_token(credentials.credentials)
        user = crud.get_user_by_email(db, email=payload["sub"])
        if not user:
            logger.warning("User not found 161")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        # Check if password meets complexity requirements
        if not validate_password(password):
            logger.warning("Password does not meet complexity requirements")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password error")
        user_update = UserUpdate(**user,password=get_password_hash(password))
        crud.update_user(db, user.username, user_update)
        logger.info(f"User {user.username} updated password")
        return JSONResponse(status_code=status.HTTP_200_OK, content="Password updated")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@user_router.patch("/auth/me/account", response_model=UserResponse, status_code=status.HTTP_200_OK)
def update_my_account(user: UserUpdate, credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """
    Update user by username
    :param db: database session
    :param username: Username
    :param user: User data
    :param credentials: Headers with token
    :return: Updated user data
    """
    verify_result = check_auth(credentials, db)
    if verify_result.status_code == status.HTTP_200_OK:
        db_user = crud.update_user(db, user_name=user.username, user=user)
        if not db_user:
            logger.warning("User not found 122")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        logger.info(f"User {user.username} updated")
        return UserResponse(**db_user.to_dict())
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@user_router.get("/auth/me/sessions", response_model=list[SessionDTO], status_code=status.HTTP_200_OK)
def get_sessions(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """
    Get all sessions for user
    :param credentials: Headers with token
    :param db: Database session
    :return: List of sessions
    """
    verify_result = check_auth(credentials, db)
    if verify_result.status_code == status.HTTP_200_OK:
        token = decode_token(credentials.credentials)
        user = crud.get_user_by_email(db, email=token["sub"])
        if not user:
            logger.warning("User not found 240")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        sessions = crud.get_sessions(user.id)
        logger.info(f"Sessions for user {user.username}: {sessions}")
        session_dtos = [SessionDTO(**session) for session in sessions]
        return session_dtos
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")

@user_router.delete("/auth/me/sessions/{session_id}")
def delete_session(session_id: str, credentials: HTTPAuthorizationCredentials = Depends(bearer),
                   db: Session = Depends(get_db)):
    """
    Delete session by ID
    :param session_id: Session ID
    :param credentials: Headers with token
    :param db: Database session
    :return: None
    """
    verify_result = check_auth(credentials, db)
    if verify_result.status_code == status.HTTP_200_OK:
        session = crud.delete_session_by_id(session_id)
        if not session:
            logger.warning("Session not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        logger.info(f"Session {session_id} was deleted")
        return JSONResponse(status_code=status.HTTP_200_OK, content="Session deleted")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")


@user_router.get("auth/me/account", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user(username: str , credentials:HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """
    Get user by username
    :param username: Username
    :param credentials: Headers with token
    :param db: Database session
    :return: User data
    """
    verify_result = check_auth(credentials, db)
    if verify_result.status_code == status.HTTP_200_OK:
        user = crud.get_user_by_username(db, username=username)
        if not user:
            logger.warning("User not found 101")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        logger.info(f"User {user.username} found")
        return UserResponse(**user.to_dict())
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


