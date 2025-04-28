import requests
from requests import Response

from src.session_service.endpoints import GET_USERS
from src.shared.logger_setup import setup_logger

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