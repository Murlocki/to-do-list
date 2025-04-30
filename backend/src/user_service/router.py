import os
import time
from datetime import datetime

from fastapi import HTTPException, status, APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from src.shared.schemas import SessionSchema, AuthResponse, SessionDTO, UserDTO, UserAuthDTO
from src.shared.logger_setup import setup_logger
from src.user_service import crud, auth_functions
from src.user_service.auth_functions import validate_password, get_password_hash, verify_password
from src.user_service.crud import authenticate_user
from src.user_service.database import SessionLocal
from src.user_service.external_functions import create_session, get_session_by_token, delete_session_by_id
from src.user_service.schemas import UserCreate, AuthForm, UserResponse, UserUpdate
from src.shared.schemas import TokenModelResponse

user_router = APIRouter()
logger = setup_logger(__name__)
logger.info(f"""
Server start time (UTC): {datetime.now()}
Server timestamp: {int(time.time())}
System timezone: {time.tzname}
Environment timezone: {os.environ.get('TZ', 'Not set')}
""")


async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()

bearer = HTTPBearer()


@user_router.post("/user/crud")
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db))->UserDTO:
    """
    Create a new user
    :param user_in: User data
    :param db: session
    :return: new UserDTO
    """
    logger.info(f"Creating new user using {user_in}")
    db_user = await crud.get_user_by_email(db, user_in.email)
    if db_user:
        logger.error(f"User with email {user_in.email} already exists")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    db_user = await crud.get_user_by_username(db, username=user_in.username)
    if db_user:
        logger.error(f"User with username {user_in.username} already exists")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already registered")
    if not validate_password(user_in.password):
        logger.warning("Password does not meet complexity requirements")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password error")
    user = await crud.create_user(db, user_in)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User creation failed")
    logger.info(f"Created new user using {user}")
    return user

@user_router.post("/user/authenticate", response_model=UserDTO, status_code=status.HTTP_200_OK)
async def auth_user(user_auth_data:UserAuthDTO,db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, user_auth_data.identifier, user_auth_data.password)
    if not user:
        logger.info("User authentication failed")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect identifier or password")
    logger.info(f"Authenticated user using {user}")
    return user


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


@user_router.get("/user")
async def get_users(db: AsyncSession = Depends(get_db)):
    """
    Get all users
    :param db:
    :return:
    """
    return await crud.get_users(db=db)


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
