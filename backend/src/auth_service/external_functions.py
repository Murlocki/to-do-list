import httpx
from src.shared.logger_setup import setup_logger
from src.shared.schemas import SessionSchema, AccessTokenUpdate, AuthResponse, UserDTO, UserAuthDTO
from src.auth_service.endpoints import CREATE_SESSION, GET_SESSION_BY_TOKEN, UPDATE_SESSION_TOKEN, DELETE_SESSION, \
    CREATE_USER, AUTHENTICATE_USER, FIND_USER_BY_EMAIL, UPDATE_USER, DELETE_SESSION_BY_TOKEN
from src.shared.schemas import SessionDTO
from src.user_service.schemas import UserCreate

logger = setup_logger(__name__)


async def create_session(session_data: SessionSchema) -> SessionDTO | None:
    """
    Create a session by forwarding data to external service.
    """
    try:
        headers = {
            "content-type": "application/json"
        }
        logger.info(f"Creating session with data: {session_data}")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                CREATE_SESSION,
                headers=headers,
                content=session_data.model_dump_json()
            )
            response.raise_for_status()
            json_data = response.json()
            return SessionDTO(**json_data)
    except httpx.RequestError as e:
        logger.error(f"An error occurred while requesting {e.request.url!r}.")
    except httpx.HTTPStatusError as e:
        logger.error(f"Error response {e.response.status_code} while requesting {e.request.url!r}.")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    return None


async def get_session_by_token(token: str, token_type: str = "access_token") -> SessionDTO | None:
    """
    Получить сессию по токену из внешнего сервиса.
    """
    try:
        headers = {
            "content-type": "application/json",
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GET_SESSION_BY_TOKEN}?token={token}&token_type={token_type}",
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            return SessionDTO(**data)
    except httpx.RequestError as e:
        logger.error(f"Request error while getting session: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")

    return None


async def update_session_token(session_id: str, access_token_update_data: AccessTokenUpdate) -> SessionDTO | None:
    try:
        headers = {
            "content-type": "application/json",
        }
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{UPDATE_SESSION_TOKEN}/{session_id}/update_token",
                headers=headers,
                content=access_token_update_data.model_dump_json()
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"Updated session token: {data}")
            return SessionDTO(**data)
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")

    return None


async def delete_session_by_id(session_id: str, access_token: str) -> AuthResponse | None:
    try:
        headers = {
            "content-type": "application/json",
            "authorization": f"bearer {access_token}"
        }
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{DELETE_SESSION}/{session_id}",
                headers=headers
            )
            response.raise_for_status()
            response_json = response.json()
            return AuthResponse(**response_json)
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    return None
async def delete_session_by_token(access_token: str) -> AuthResponse | None:
    try:
        headers = {
            "content-type": "application/json",
            "authorization": f"bearer {access_token}"
        }
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{DELETE_SESSION_BY_TOKEN}?token={access_token}",
                headers=headers
            )
            response.raise_for_status()
            response_json = response.json()
            return AuthResponse(**response_json)
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    return None

async def create_user(user: UserCreate) -> UserDTO | None:
    headers = {
        "content-type": "application/json",
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{CREATE_USER}",
                headers=headers,
                content=user.model_dump_json()
            )
            response.raise_for_status()  # выбросит исключение, если ошибка
            logger.info(f"Created new user: {user}")
            return UserDTO(**response.json())
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 409:
            raise e
        logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
    return None

async def authenticate_user(user: UserAuthDTO) -> UserDTO | None:
    try:
        headers = {
            "content-type": "application/json",
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AUTHENTICATE_USER}",
                headers=headers,
                content=user.model_dump_json()
            )
            response.raise_for_status()
            logger.info(f"Authenticated user: {user}")
            return UserDTO(**response.json())
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
    return None

async def find_user_by_email(email:str) -> UserDTO | None:
    try:
        headers = {
            "content-type": "application/json",
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{FIND_USER_BY_EMAIL}?email={email}",
                headers=headers,
            )
            response.raise_for_status()
            logger.info(f"Find user by email: {email}")
            return UserDTO(**response.json())
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
    return None

async def update_user(user: UserDTO, access_token:str) -> AuthResponse | None:
    try:
        headers = {
            "content-type": "application/json",
            "authorization": f"bearer {access_token}"
        }
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{UPDATE_USER}",
                headers=headers,
                content=user.model_dump_json()
            )
            response.raise_for_status()
            logger.info(f"Update user {user.username} by token {access_token}")
            return AuthResponse(**response.json())
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
    return None
