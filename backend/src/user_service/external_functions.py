import requests
from src.shared.logger_setup import setup_logger
from src.shared.schemas import SessionSchema, AccessTokenUpdate
from src.user_service.endpoints import CREATE_SESSION, GET_SESSION_BY_TOKEN, UPDATE_SESSION_TOKEN
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

def get_session_by_token(token:str, token_type:str="access_token")->SessionDTO:
    """
    Get all users from external service
    :return: list of users
    """
    try:
        headers = {
            "content-type": "application/json",
        }
        response = requests.get(f"{GET_SESSION_BY_TOKEN}?token={token}&token_type={token_type}", headers=headers)
        logger.warning(response)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(e)

def update_session_token(session_id:str, access_token_update_data: AccessTokenUpdate)->SessionDTO:
    """
    Get all users from external service
    :return: list of users
    """
    try:
        headers = {
            "content-type": "application/json",
        }
        response = requests.patch(f"{UPDATE_SESSION_TOKEN}/{session_id}/update_token", headers=headers, data=access_token_update_data.model_dump_json())
        logger.warning(response)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(e)