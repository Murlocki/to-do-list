import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.user_service.as_tasks import startup_event, shutdown_event
from src.user_service.logger_setup import setup_logger
from src.user_service.router import user_router

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    # Load the routine
    await startup_event(fastapi_app)
    yield
    # Clean up release the resources
    await shutdown_event(fastapi_app)
    logger.warning("Shutdown event triggered")


app = FastAPI(lifespan=lifespan)
app.include_router(user_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


import httpx
from fastapi import HTTPException


async def proxy_request(external_url: str, method: str, headers: dict, data: dict = None):
    async with httpx.AsyncClient(timeout=10) as client:
        # Проксируем запрос к внешнему сервису
        if method.lower() == "get":
            response = await client.get(external_url, headers=headers, params=data)
        elif method.lower() == "post":
            response = await client.post(external_url, headers=headers, json=data)
        elif method.lower() == "put":
            response = await client.put(external_url, headers=headers, json=data)
        elif method.lower() == "patch":
            response = await client.patch(external_url, headers=headers, json=data)
        elif method.lower() == "delete":
            response = await client.delete(external_url, headers=headers)
        else:
            raise HTTPException(status_code=400, detail="Invalid HTTP method")

        # Возвращаем ответ от внешнего сервиса
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.json()
        }


async def get_all_users():
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhdXRoLXNlcnZpY2UiLCJzdWIiOiJqb2huLmRvZUBleGFtcGxlLmNvbSIsImp0aSI6IjFjNjVjODQ4LTQ4NGEtNGQxYS1iMWQ3LWExMmI3NTE4ZmZjNyIsImV4cCI6MTc0NTkwNjAyNC45OTY0NTMsImlhdCI6MTc0NTc5Nzk5NH0.rCnQEwQdu3UIqJHxGwYW8USEE3wlXwYBgznXTTW4WcM"
    }
    users = await proxy_request(f"http://127.0.0.1:8000/auth/check_auth", "GET", headers=headers)
    print(users)


if __name__=="__main__":
    asyncio.run(get_all_users())
