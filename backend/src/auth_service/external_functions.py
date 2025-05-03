import httpx
from httpx import Response

from src.auth_service.endpoints import CREATE_SESSION, GET_SESSION_BY_TOKEN, UPDATE_SESSION_TOKEN, DELETE_SESSION, \
    CREATE_USER, AUTHENTICATE_USER, FIND_USER_BY_EMAIL, UPDATE_USER, DELETE_SESSION_BY_TOKEN, UPDATE_USER_PASSWORD, \
    GET_USER_SESSIONS
from src.shared.logger_setup import setup_logger
from src.shared.schemas import PasswordForm
from src.shared.schemas import SessionSchema, AccessTokenUpdate, UserDTO, UserAuthDTO
from src.user_service.schemas import UserCreate

logger = setup_logger(__name__)


async def create_session(session_data: SessionSchema) -> Response:
    """
    Create a session by forwarding data to external service.
    :param session_data: Session data
    :return: response from external service
    """
    headers = {
        "content-type": "application/json",
    }
    logger.info(f"Creating session with data: {session_data}")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            CREATE_SESSION,
            headers=headers,
            content=session_data.model_dump_json()
        )
        logger.info(f"Created session with response: {response.json()}")
        return response


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


async def update_session_token(session_id: str, access_token_update_data: AccessTokenUpdate) -> Response:
    """
    Update session token by forwarding data to external service.
    :param session_id: session id for updating session
    :param access_token_update_data: new access token update data
    :return: response from external service
    """
    headers = {
        "content-type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{UPDATE_SESSION_TOKEN}/{session_id}/update_token",
            headers=headers,
            content=access_token_update_data.model_dump_json()
        )
        logger.info(f"Updated session token: {response.json()}")
        return response


async def delete_session_by_id(session_id: str, access_token: str, skip_auth: bool = False) -> Response:
    """
    Delete session by id
    :param session_id: session id for deleting
    :param access_token: access token for auth
    :param skip_auth: need check auth in method
    :return: response from external service
    """
    async with httpx.AsyncClient() as client:
        headers = {
            "content-type": "application/json",
            "authorization": f"bearer {access_token}",
            "X-Skip-Auth": str(skip_auth),
        }
        response = await client.delete(
            f"{DELETE_SESSION}/{session_id}",
            headers=headers
        )
        logger.info(f"Deleted session {session_id} with response: {response.json()}")
        return response


async def delete_sessions_by_token(access_token: str, skip_auth: bool = False) -> Response:
    """
    Delete session by token
    :param access_token: token for finding session
    :param skip_auth: need check auth in method
    :return: response from external service
    """
    headers = {
        "content-type": "application/json",
        "authorization": f"bearer {access_token}",
        "X-Skip-Auth": str(skip_auth),
    }
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{DELETE_SESSION_BY_TOKEN}",
            headers=headers
        )
        logger.info(f"Deleted sessions by token {access_token} with response {response.json()}")
        return response


async def create_user(user: UserCreate) -> Response:
    """
    Create new user
    :param user: UserCreate object for creating new user
    :return: response from external service
    """
    headers = {
        "content-type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{CREATE_USER}",
            headers=headers,
            content=user.model_dump_json()
        )
        logger.info(f"Created new user: {user}")
        return response


async def authenticate_user(user: UserAuthDTO) -> Response:
    """
    Authenticate user
    :param user: User identifier and password
    :return: Auth response
    """
    headers = {
        "content-type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AUTHENTICATE_USER}",
            headers=headers,
            content=user.model_dump_json()
        )
        logger.info(f"Authenticated user response {response.json()}")
        return response


async def find_user_by_email(email: str) -> Response:
    """
    Find user by email
    :param email: email for finding user
    :return: response from external service
    """
    headers = {
        "content-type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{FIND_USER_BY_EMAIL}?email={email}",
            headers=headers,
        )
        logger.info(f"Find user by email: {email} with response {response.json()}")
        return response


async def update_user(user: UserDTO, access_token: str, skip_auth: bool = False) -> Response:
    """
    Update user
    :param user: UserDTO for updating
    :param access_token: access token for auth
    :param skip_auth: need check auth in method
    :return: response from external service
    """
    headers = {
        "content-type": "application/json",
        "authorization": f"bearer {access_token}",
        "X-Skip-Auth": str(skip_auth),
    }
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{UPDATE_USER}",
            headers=headers,
            content=user.model_dump_json()
        )
        logger.info(f"Update user {user.username} by token {access_token} with response {response.json()}")
        return response


async def update_user_password(password_form: PasswordForm, access_token: str, skip_auth: bool = False) -> Response:
    """
    Update user password
    :param password_form: password form with new password
    :param access_token: access token for auth
    :param skip_auth: need check auth in method
    :return: response from external service
    """
    headers = {
        "content-type": "application/json",
        "authorization": f"bearer {access_token}",
        "X-Skip-Auth": str(skip_auth),
    }
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{UPDATE_USER_PASSWORD}",
            headers=headers,
            content=password_form.model_dump_json()
        )
        logger.info(f"Get reponse from update user password: {response.json()}")
        return response

async def get_user_sessions(user_id:int) -> Response:
    """
    Get user sessions
    :param user_id: User id
    :return: Response from external service
    """
    headers = {
        "content-type": "application/json"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GET_USER_SESSIONS}/{user_id}",
            headers=headers
        )
        logger.info(f"Get reponse from get user sessions: {response.json()}")
        return response