import os
import time
from datetime import datetime

from fastapi import HTTPException, status, APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.responses import JSONResponse


from src.session_service import crud
from src.session_service.crud import create_and_store_session, delete_inactive_sessions, update_session_access_token
from src.session_service.external_functions import check_auth_from_external_service, decode_token
from src.shared import logger_setup
from src.shared.schemas import SessionDTO, AccessTokenUpdate
from src.shared.schemas import SessionSchema

session_router = APIRouter()
logger = logger_setup.setup_logger(__name__)
logger.info(f"""
Server start time (UTC): {datetime.utcnow()}
Server timestamp: {int(time.time())}
System timezone: {time.tzname}
Environment timezone: {os.environ.get('TZ', 'Not set')}
""")



bearer = HTTPBearer()


@session_router.get("/session/crud/me", response_model=list[SessionDTO], status_code=status.HTTP_200_OK)
def get_sessions(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    """
    Get all sessions for user
    :param credentials: Headers with token
    :param db: Database session
    :return: List of sessions
    """
    verify_result = check_auth_from_external_service(credentials.credentials)
    if verify_result:
        token = decode_token(credentials.credentials)
        # TODO: ПЕРЕНЕСТИ ПОЛУЧЕНИЕ ПОЛЬЗОВАТЕЛЯ В ВНЕШНЮЮ СИСТЕМУ
        user = crud.get_user_by_email(email=token["sub"])
        if not user:
            logger.warning("User not found 240")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        delete_inactive_sessions(user_id=user.id)
        sessions = crud.get_sessions(user_id=user.id)
        logger.info(f"Sessions for user {user.username}: {sessions}")
        session_dtos = [SessionDTO(**session) for session in sessions]
        return session_dtos
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@session_router.delete("/session/crud/{session_id}")
def delete_session(session_id: str, credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    """
    Delete session by ID
    :param session_id: Session ID
    :param credentials: Headers with token
    :return: None
    """
    verify_result = check_auth_from_external_service(credentials.credentials)
    if verify_result:
        session = crud.delete_session_by_id(session_id)
        if not session:
            logger.warning("Session not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        logger.info(f"Session {session_id} was deleted")
        return JSONResponse(status_code=status.HTTP_200_OK, content="Session deleted")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@session_router.patch("/session/crud/{session_id}/update_token", response_model=SessionDTO, status_code=status.HTTP_200_OK)
def update_session_token(session_id: str, access_token_update_data: AccessTokenUpdate):
    """
    Update session token
    :param access_token_update_data:
    :param session_id: Session ID
    :return: New session entity
    """
    session = get_session_by_token(access_token_update_data.old_access_token)
    if not session:
        logger.warning("Session not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session["session_id"] != session_id:
        logger.warning("Session ID does not match")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session ID does not match")
    session = update_session_access_token(access_token_update_data.old_access_token, access_token_update_data.new_access_token)
    if not session:
        logger.warning("Session not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    logger.info(f"Session {session_id} was updated")
    return session

@session_router.post("/session/crud", response_model=SessionDTO, status_code=status.HTTP_201_CREATED)
def create_session(session_create_data:SessionSchema):
    """
    Create new session
    :param session_create_data:
    :return: Created session
    """
    logger.warning(session_create_data)
    return create_and_store_session(
        user_id=session_create_data.user_id,
        access_token=session_create_data.access_token,
        refresh_token=session_create_data.refresh_token,
        device=session_create_data.device,
        ip_address=session_create_data.ip_address
    )

@session_router.get("/session/crud/search", response_model=SessionDTO, status_code=status.HTTP_200_OK)
def get_session_by_token(token: str, token_type: str = "access_token"):
    """
    Get session by token
    :param token: session token
    :param token_type: access_token or refresh_token
    :return: dict|None
    """
    session = crud.get_session_by_token(token, token_type)
    if not session:
        logger.warning("Session not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    logger.info(f"Session {session['session_id']} was found")
    return session

