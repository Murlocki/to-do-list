import httpx


from fastapi.responses import JSONResponse
from src.shared.logger_setup import setup_logger
from src.shared.schemas import SessionSchema, AccessTokenUpdate, AuthResponse
from src.user_service.endpoints import CREATE_SESSION, GET_SESSION_BY_TOKEN, UPDATE_SESSION_TOKEN, DELETE_SESSION
from src.shared.schemas import SessionDTO

logger = setup_logger(__name__)

async def create_session(session_data: SessionSchema) -> SessionDTO | None:
    """
    Create a session by forwarding data to external service.
    """
    try:
        headers = {
            "content-type": "application/json"
        }
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
            return data
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")

    return None

async def delete_session_by_id(session_id: str, access_token:str) -> AuthResponse | None:
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
            return response_json
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")

    return None