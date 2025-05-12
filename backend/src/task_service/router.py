import os
import time
from datetime import datetime

from fastapi import HTTPException, status, APIRouter, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.session_service.external_functions import check_auth_from_external_service, find_user_by_email
from src.shared import logger_setup
from src.shared.common_functions import decode_token, verify_response
from src.shared.database import SessionLocal
from src.shared.schemas import AuthResponse, UserDTO, TaskDTO
from src.task_service import crud
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
    :param task_data:
    :param token: User token
    :param db: session
    :return: new TaskDTO
    """
    logger.info(task_data)
    payload = decode_token(token)
    result = AuthResponse(token=token, data={"message":""})
    if not payload or not payload["sub"]:
        logger.error("Invalid token payload")
        result.data = {"message": "Invalid token payload"}
        raise HTTPException(status_code=401, detail=result.model_dump())
    logger.info(f"Decoded token payload: {payload}")

    response = await find_user_by_email(payload["sub"])
    error = verify_response(response)
    if error:
        logger.error(f"Error finding user by email: {error}")
        result.data = {"message": f"Error finding user by email: {error['detail']}"}
        raise HTTPException(status_code=error["status"], detail=result.model_dump())
    user = UserDTO(**response.json())
    logger.info(f"User found: {user}")

    task = await crud.create_task(task_data, user.id, db)
    if not task:
        logger.error("Task creation failed")
        result.data = {"message": "Task creation failed"}
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.model_dump())
    logger.info(f"Task created: {task}")
    return AuthResponse(
        token=token,
        data=task.to_dict(),
    ).model_dump(by_alias=True)
@task_router.get("/task/me", status_code=status.HTTP_200_OK, response_model=AuthResponse)
async def get_tasks_me(token:str = Depends(get_valid_token),db: AsyncSession = Depends(get_db)):
    """
    Get tasks for the current user
    :param token: User token
    :param db: session
    :return: list of TaskDTO
    """
    payload = decode_token(token)
    result = AuthResponse(token=token, data={"message": ""})
    if not payload or not payload["sub"]:
        result.data = {"message": "Invalid or expired token"}
        logger.error("Invalid token payload")
        raise HTTPException(status_code=401, detail=result.model_dump())
    logger.info(f"Decoded token payload: {payload}")

    response = await find_user_by_email(payload["sub"])
    error = verify_response(response)
    if error:
        logger.error(f"Error finding user by email: {error}")
        result.data = {"message": f"Error finding user by email: {error['detail']}"}
        raise HTTPException(status_code=error["status"], detail=result.model_dump())
    user = UserDTO(**response.json())
    logger.info(f"User found: {user}")

    tasks = await crud.get_tasks_by_user_id(db, user.id)
    logger.info(f"Tasks retrieved: {tasks}")
    return AuthResponse(
        token=token,
        data=[TaskDTO(**task.to_dict()) for task in tasks],
    ).model_dump(by_alias=True)

@task_router.delete("/task/me/{task_id}", status_code=status.HTTP_200_OK, response_model=AuthResponse)
async def delete_task_by_id(task_id: int, token: str = Depends(get_valid_token), db: AsyncSession = Depends(get_db)):
    """
    Delete task by ID
    :param task_id: Task ID
    :param token: User token
    :param db: session
    :return: deleted TaskDTO
    """
    payload = decode_token(token)
    result = AuthResponse(token=token, data={"message": ""})
    if not payload or not payload["sub"]:
        result.data = {"message": "Invalid or expired token"}
        logger.error("Invalid token payload")
        raise HTTPException(status_code=401, detail=result)
    logger.info(f"Decoded token payload: {payload}")

    response = await find_user_by_email(payload["sub"])
    error = verify_response(response)
    if error:
        logger.error(f"Error finding user by email: {error}")
        result.data = {"message": f"Error finding user by email: {error['detail']}"}
        raise HTTPException(status_code=error["status"], detail=result.model_dump())
    user = UserDTO(**response.json())
    logger.info(f"User found: {user}")

    task = await crud.delete_task_by_id(db, task_id)
    if not task:
        logger.error("Task deletion failed")
        result.data = {"message": "Task deletion failed"}
        raise HTTPException(status_code=404, detail=result.model_dump())
    logger.info(f"Task deleted: {task}")
    return AuthResponse(
        token=token,
        data=task.to_dict(),
    ).model_dump(by_alias=True)

@task_router.patch("/task/me/{task_id}", status_code=status.HTTP_200_OK, response_model=AuthResponse)
async def update_task_by_id(task_id: int, task_data: TaskCreate, token: str = Depends(get_valid_token), db: AsyncSession = Depends(get_db)):
    """
    Update task by ID
    :param task_id: Task ID
    :param task_data: Task data to update
    :param token: User token
    :param db: session
    :return: updated TaskDTO
    """
    payload = decode_token(token)
    result = AuthResponse(token=token, data={"message": ""})
    if not payload or not payload["sub"]:
        result.data = {"message": "Invalid or expired token"}
        logger.error("Invalid token payload")
        raise HTTPException(status_code=401, detail=result.model_dump())
    logger.info(f"Decoded token payload: {payload}")


    response = await find_user_by_email(payload["sub"])
    error = verify_response(response)
    if error:
        logger.error(f"Error finding user by email: {error}")
        result.data = {"message": f"Error finding user by email: {error['detail']}"}
        raise HTTPException(status_code=error["status"], detail=result.model_dump())
    user = UserDTO(**response.json())
    logger.info(f"User found: {user}")

    task = await crud.get_task_by_id(db, task_id)
    if task.version > task_data.version:
        logger.error(f"Task {task.to_dict()} was already updated")
        result.data = {"message": f"Task was already updated"}
        raise HTTPException(status_code=400, detail=result.model_dump())

    task = await crud.update_task_by_id(db, task_id, task_data)
    if not task:
        logger.error("Task update failed")
        result.data = {"message": "Task update failed"}
        raise HTTPException(status_code=404, detail=result.model_dump())
    logger.info(f"Task updated: {task}")
    return AuthResponse(
        token=token,
        data=task.to_dict(),
    ).model_dump(by_alias=True)