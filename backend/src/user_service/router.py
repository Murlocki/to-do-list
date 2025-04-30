import os
import time
from datetime import datetime

from fastapi import HTTPException, status, APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from src.shared.schemas import SessionSchema, AuthResponse, SessionDTO
from src.auth_service import logger_setup, crud, auth_functions
from src.auth_service.auth_functions import validate_password, decode_token, \
    verify_and_refresh_access_token, get_password_hash
from src.auth_service.database import SessionLocal
from src.auth_service.external_functions import create_session, get_session_by_token, delete_session_by_id
from src.auth_service.schemas import UserCreate, AuthForm, UserResponse, UserUpdate
from src.shared.schemas import TokenModelResponse

user_router = APIRouter()
logger = logger_setup.setup_logger(__name__)
logger.info(f"""
Server start time (UTC): {datetime.now()}
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


# TODO: Вынести в отдельный сервис по стуки к пользователям
@user_router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
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
    return result


@user_router.post("/auth/login", response_model=TokenModelResponse, status_code=status.HTTP_200_OK)
async def login_user(auth_form: AuthForm, db: Session = Depends(get_db)):
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
        session_data = await create_session(
            SessionSchema(user_id=user.id, access_token=access_token, refresh_token=refresh_token,
                          device=auth_form.device, ip_address=auth_form.ip_address))
        if not session_data:
            logger.warning("Session not created")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session not created")
        logger.info(f"User logged in (rem mode): {user.email}")
        # TODO: Оставить в ответе только access_token и token_type, остальное удалить ибо не нужно клиенту
        return {"token": access_token}
    else:
        session_data = await create_session(
            SessionSchema(
                user_id=user.id,
                access_token=access_token,
                device=auth_form.device,
                ip_address=auth_form.ip_address))
        if not session_data:
            logger.warning("Session not created")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session not created")
        logger.info(f"User logged in: {user.email}")
        return {"token"}


@user_router.get("/user/{username}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(username: str, credentials: HTTPAuthorizationCredentials = Depends(bearer),
                   db: Session = Depends(get_db)):
    """
    Get user by username
    :param username: Username
    :param credentials: Headers with token
    :param db: Database session
    :return: User data
    """
    verify_result = await check_auth(credentials, db)
    if verify_result:
        user = crud.get_user_by_username(db, username=username)
        if not user:
            logger.warning("User not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        logger.info(f"User {user.username} found")
        return UserResponse(**user.to_dict())
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@user_router.post("/auth/logout", status_code=status.HTTP_200_OK, response_model=AuthResponse)
async def logout_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    # Check if token is valid
    token_verified = await check_auth(credentials, next(get_db()))
    logger.info(token_verified)
    if not token_verified or not token_verified["token"]:
        logger.warning("Invalid token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=AuthResponse(data={"message": "Invalid token"}, token=credentials.credentials))
    token = token_verified["token"]
    result = AuthResponse(data={"message": ""}, token=token)
    logger.info(f"Valid Token: {token}")
    # Get session by token
    session: SessionDTO = await get_session_by_token(token, token_type="access_token")
    if not session:
        result.data = {"message": "Session not found"}
        logger.warning("Session not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result)
    logger.info(f"Found session {session}")
    # Delete session
    response_json = await delete_session_by_id(session.session_id, token)
    if not response_json:
        result.data = {"message": "Session delete error"}
        logger.warning("Session delete error")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result)
    logger.info(f"Session {session.session_id} deleted")
    result.data = response_json
    return result


@user_router.get("/auth/check_auth", response_model=TokenModelResponse)
# TODO: УБРАТЬ БД ОТСЮДА НАХРЕН
async def check_auth(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
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

    # TODO: ВЫНЕСТИ ПО СТУК ПО EMAIL В СЕРВИС ПОЛЬЗОВАТЕЛЕЙ
    # Get token user
    user = crud.get_user_by_email(db, email=payload["sub"])
    if not user:
        logger.warning("User not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "User is not found",
                                                                           "token": None})

    # Check token validity and refresh if needed
    token = await verify_and_refresh_access_token(token)
    if not token:
        logger.warning("Invalid new token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"message": "Invalid new token",
                                                                              "token": None})
    return {"token": token}


@user_router.get("/user")
def get_users(db: Session = Depends(get_db)):
    """
    Get all users
    :param db:
    :return:
    """
    return crud.get_users(db=db)


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
def update_password(password: str, credentials: HTTPAuthorizationCredentials = Depends(bearer),
                    db: Session = Depends(get_db)):
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
        user_update = UserUpdate(**user, password=get_password_hash(password))
        crud.update_user(db, user.username, user_update)
        logger.info(f"User {user.username} updated password")
        return JSONResponse(status_code=status.HTTP_200_OK, content="Password updated")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@user_router.patch("/auth/me/account", response_model=UserResponse, status_code=status.HTTP_200_OK)
def update_my_account(user: UserUpdate, credentials: HTTPAuthorizationCredentials = Depends(bearer),
                      db: Session = Depends(get_db)):
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
