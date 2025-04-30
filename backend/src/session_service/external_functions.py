import httpx
from jose import jwt, JWTError
from fastapi.responses import JSONResponse

from src.session_service.config import settings
from src.session_service.endpoints import GET_USERS, CHECK_AUTH, FIND_USER_BY_EMAIL
from src.shared.logger_setup import setup_logger
from src.shared.schemas import TokenModelResponse, UserDTO

logger = setup_logger(__name__)

async def get_users_from_external_service():
    """
    Get all users from external service
    :return: list of users
    """
    try:
        headers = {
            "content-type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(GET_USERS, headers=headers)
            response.raise_for_status()
            json_data = response.json()
            return json_data
    except httpx.RequestError as e:
        logger.error(f"An error occurred while requesting {e.request.url!r}.")
    except httpx.HTTPStatusError as e:
        logger.error(f"Error response {e.response.status_code} while requesting {e.request.url!r}.")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    return None


async def check_auth_from_external_service(access_token: str) -> TokenModelResponse | None:
    """
    Check auth
    :param access_token:
    :return: json - token old or new
    """
    try:
        headers = {
            "content-type": "application/json",
            "authorization": f"Bearer {access_token}"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(CHECK_AUTH, headers=headers)
            response.raise_for_status()  # Проверяем статусный код на ошибки
            json_data = response.json()
            return json_data
    except httpx.RequestError as e:
        logger.error(f"An error occurred while requesting {e.request.url!r}.")
    except httpx.HTTPStatusError as e:
        logger.error(f"Error response {e.response.status_code} while requesting {e.request.url!r}.")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
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

def decode_token(token: str, is_refresh: bool = False) -> dict[str, any] | None:
    """
    Decode token
    :param token: Token for decode
    :param is_refresh: True if it is refresh token
    :return: dict[str, any] | None: Decoded token payload or None if error
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret_refresh if is_refresh else settings.jwt_secret,
                             algorithms=settings.jwt_algorithm, options={"verify_exp": False})
        logger.info(f"Token decoded successfully: {payload}")
        return payload
    except JWTError as e:
        logger.warning(f"JWTError: {e}")
        return None