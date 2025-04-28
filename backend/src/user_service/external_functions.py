import requests
from src.shared.logger_setup import setup_logger
from src.shared.schemas import SessionSchema
from src.user_service.endpoints import CREATE_SESSION
from src.user_service.schemas import SessionDTO

logger = setup_logger(__name__)

def create_session(session_data:SessionSchema)->SessionDTO:
    """
    Get all users from external service
    :return: list of users
    """
    try:
        headers = {
            "content-type": "application/json",
            # если нужен токен, добавь сюда Authorization
        }
        logger.warning(session_data)
        response = requests.post(CREATE_SESSION, headers=headers, data=session_data.model_dump_json())
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(e)
