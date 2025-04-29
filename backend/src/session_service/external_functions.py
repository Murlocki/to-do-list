import requests
from jose import jwt, JWTError
from requests import Response

from src.session_service.config import settings
from src.session_service.endpoints import GET_USERS
from src.shared.logger_setup import setup_logger
from src.shared.schemas import TokenModelResponse

logger = setup_logger(__name__)

def get_users_from_external_service()->Response:
    """
    Get all users from external service
    :return: list of users
    """
    try:
        headers = {
            "content-type": "application/json",
            # если нужен токен, добавь сюда Authorization
        }

        response = requests.get(GET_USERS, headers=headers)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        logger.error(e)

def check_auth_from_external_service(access_token: str)->TokenModelResponse:
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
        response = requests.get(GET_USERS, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(e)

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