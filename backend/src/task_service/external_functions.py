import httpx
from httpx import Response

from src.session_service.endpoints import CHECK_AUTH
from src.shared.logger_setup import setup_logger
from src.shared.schemas import TokenModelResponse
from src.task_service.endpoints import GET_SESSION_BY_TOKEN

logger = setup_logger(__name__)



async def check_auth_from_external_service(access_token: str, skip_auth: bool = False) -> TokenModelResponse | None:
    """
    Check auth
    :param skip_auth:
    :param access_token:
    :return: json - token old or new
    """
    try:
        headers = {
            "content-type": "application/json",
            "authorization": f"Bearer {access_token}",
            "X-Skip-Auth": str(skip_auth)
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

async def get_session_by_token(token: str, token_type: str = "access_token") -> Response:
    """
    Получить сессию по токену из внешнего сервиса.
    :param token: Token for finding session
    :param token_type: Token type for finding session
    :return response: Response from external service
    """
    headers = {
        "content-type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GET_SESSION_BY_TOKEN}?token={token}&token_type={token_type}",
            headers=headers
        )
        logger.info(f"Get session by token {token} with type {token_type} with response: {response.json()}")
        return response