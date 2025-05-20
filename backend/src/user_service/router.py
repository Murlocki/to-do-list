import os
import time
from datetime import datetime

from fastapi import HTTPException, status, APIRouter, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.common_functions import decode_token, verify_response
from src.shared.database import SessionLocal
from src.shared.logger_setup import setup_logger
from src.shared.models import User
from src.shared.schemas import AuthResponse, UserAuthDTO
from src.shared.schemas import UserDTO, PasswordForm
from src.user_service import crud, auth_functions
from src.user_service.auth_functions import validate_password, get_password_hash
from src.user_service.external_functions import check_auth_from_external_service, delete_user_sessions
from src.user_service.schemas import UserCreate, UserUpdate

user_router = APIRouter()
logger = setup_logger(__name__)
logger.info(f"""
Server start time (UTC): {datetime.now()}
Server timestamp: {int(time.time())}
System timezone: {time.tzname}
Environment timezone: {os.environ.get('TZ', 'Not set')}
""")

bearer = HTTPBearer()


async def get_valid_token(request:Request, credentials: HTTPAuthorizationCredentials = Depends(bearer)) -> str:
    if request.headers.get("X-Skip-Auth") == "True":
        logger.info("Skip authentication check")
        return credentials.credentials
    verify_result = await check_auth_from_external_service(credentials.credentials)
    logger.info(f"Verify result {verify_result}")
    if not verify_result or not verify_result["token"]:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return verify_result["token"]


async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()


bearer = HTTPBearer()


@user_router.post("/user/crud", status_code=status.HTTP_201_CREATED, response_model=UserDTO)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)) -> UserDTO:
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
    if not auth_functions.validate_password(user_in.password):
        logger.warning("Password does not meet complexity requirements")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password error")
    user = await crud.create_user(db, user_in)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User creation failed")
    logger.info(f"Created new user using {user}")
    return user


@user_router.post("/user/authenticate", response_model=UserDTO, status_code=status.HTTP_200_OK)
async def auth_user(user_auth_data: UserAuthDTO, db: AsyncSession = Depends(get_db)):
    user = await crud.authenticate_user(db, user_auth_data.identifier, user_auth_data.password)
    if not user:
        logger.info("User authentication failed")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect identifier or password")
    logger.info(f"Authenticated user using {user}")
    return user


@user_router.get("/user/crud/search", status_code=status.HTTP_200_OK, response_model=UserDTO)
async def search_user(email: str, db: AsyncSession = Depends(get_db)):
    logger.info(f"Searching user using {email}")
    user = await crud.get_user_by_email(db, email)
    if not user:
        logger.info(f"User with email {email} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    logger.info(f"User with email {email} found")
    return user


@user_router.get("/user/me", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def get_profile(token: str = Depends(get_valid_token), db: AsyncSession = Depends(get_db)):
    """
    Get user by token (basically gey my profile)
    :param token: User access token
    :param db: Database session
    :return: User data
    """
    result = AuthResponse(token=token, data={"message": "User not found"})
    payload = decode_token(token)
    if not payload or not payload["sub"]:
        logger.info(f"Invalid token")
        result.data = {"message": "Invalid token"}
        raise HTTPException(status_code=401, detail=result.model_dump())

    user = await crud.get_user_by_email(db, email=payload["sub"])
    if not user:
        logger.warning("User not found")
        result.data = {"message": "User not found"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.model_dump())
    logger.info(f"User {user.username} found")
    result.data = UserDTO.model_validate(user)
    return result.model_dump(by_alias=True)


@user_router.delete("/user/me", status_code=status.HTTP_200_OK, response_model=AuthResponse)
async def delete_me(token: str = Depends(get_valid_token), db: AsyncSession = Depends(get_db)):
    """
    Delete of my self
    :param token: User access token
    :param db: Database session
    :return: None
    """
    decoded_token = decode_token(token)
    result = AuthResponse(token=token, data={"message": ""})
    user: User = await crud.get_user_by_email(db, email=decoded_token["sub"])
    if not user:
        logger.warning("User not found")
        result.data["message"] = "User not found"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.model_dump())
    user = await crud.delete_user(db, user)
    if not user:
        logger.warning("User not found")
        result.data["message"] = "User not found"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.model_dump())
    logger.info(f"User {user.username} deleted")
    result.data = UserDTO.model_validate(user)
    return result.model_dump()


@user_router.patch("/user/me/password", status_code=status.HTTP_200_OK, response_model=AuthResponse)
async def update_password(password_form: PasswordForm, token: str = Depends(get_valid_token),
                          db: AsyncSession = Depends(get_db)):
    """
    Update user password
    :param password_form: New password
    :param token: Access token
    :param db: Database session
    :return: None
    """
    result = AuthResponse(token=token, data={"message": "Password updated"})
    payload = decode_token(token)
    logger.info(f"Decode token {payload}")
    user: User = await crud.get_user_by_email(db, email=payload["sub"])
    if not user:
        logger.warning("User not found")
        result.data["message"] = "User not found"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.model_dump())
    logger.info(f"User {user.to_dict()} is found")
    # Check if password meets complexity requirements
    if not validate_password(password_form.new_password):
        logger.warning("Password does not meet complexity requirements")
        result.data["message"] = "Password does not meet complexity requirements"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.model_dump())
    logger.info(f"Password validated {password_form.new_password}")
    # Update user password
    user_update = UserUpdate(**user.to_dict(), password=password_form.new_password)
    logger.info(f"Update user:{user_update}")
    user_update = await crud.update_user(db, user.username, user_update)
    logger.info(f"User {user_update.username} updated password {user_update.hashed_password}")

    response = await delete_user_sessions(token, skip_auth=True)
    error = verify_response(response)
    if error:
        logger.error(f"Error {error}")
        result.data["message"] = error["detail"]["message"]
        raise HTTPException(status_code=error["status"], detail=result.model_dump())
    logger.info(f"User sessions deleted {response.json()}")
    return AuthResponse(data=UserDTO(**user_update.to_dict()), token=token).model_dump()


@user_router.patch("/user/me/account", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def update_my_account(user: UserUpdate, token: str = Depends(get_valid_token), db: AsyncSession = Depends(get_db)):
    """
    Update user by username
    :param db: database session
    :param user: User data
    :param token: Access token
    :return: Updated user data
    """
    db_user = await crud.update_user(db, user_name=user.username, user=user)
    if not db_user:
        logger.warning("User not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=AuthResponse(token=token,
                                                data={
                                                    "message": "User not found"}).model_dump())
    logger.info(f"User {user.username} updated")
    return AuthResponse(token=token, data=UserDTO(**db_user.to_dict()))
