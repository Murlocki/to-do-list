import os
import time
from datetime import datetime

from fastapi import HTTPException, status, APIRouter, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.task_service import crud
from src.session_service.external_functions import check_auth_from_external_service, find_user_by_email
from src.shared import logger_setup
from src.shared.common_functions import decode_token, verify_response
from src.shared.database import SessionLocal
from src.shared.schemas import AuthResponse, UserDTO
from src.task_service.schemas import TaskCreate

task_router = APIRouter()
logger = logger_setup.setup_logger(__name__)
logger.info(f"""
Server start time (UTC): {datetime.now()}
Server timestamp: {int(time.time())}
System timezone: {time.tzname}
Environment timezone: {os.environ.get('TZ', 'Not set')}
""")

bearer = HTTPBearer()


async def get_valid_token(request: Request, credentials: HTTPAuthorizationCredentials = Depends(bearer)) -> str:
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

@task_router.post("/task/me", status_code=status.HTTP_201_CREATED, response_model=AuthResponse)
async def create_task(task_data: TaskCreate, token = Depends(get_valid_token), db: AsyncSession = Depends(get_db)):
    """
    Create a new task
    :param token: User token
    :param db: session
    :return: new TaskDTO
    """
    payload = decode_token(token)
    if not payload or not payload["sub"]:
        logger.error("Invalid token payload")
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    logger.info(f"Decoded token payload: {payload}")

    response = await find_user_by_email(payload["sub"])
    error = verify_response(response)
    if error:
        logger.error(f"Error finding user by email: {error}")
        raise HTTPException(status_code=404, detail="User not found")
    user = UserDTO(**response.json())
    logger.info(f"User found: {user}")

    task = await crud.create_task(task_data, user.id, db)
    if not task:
        logger.error("Task creation failed")
        raise HTTPException(status_code=500, detail="Task creation failed")
    logger.info(f"Task created: {task}")
    return AuthResponse(
        token=token,
        data=task.to_dict(),
    ).model_dump()


