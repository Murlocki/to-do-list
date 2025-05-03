import uuid
from copy import deepcopy
from datetime import timedelta, datetime

from jose import jwt, JWTError

from src.auth_service.external_functions import get_session_by_token, update_session_token, create_session
from src.auth_service.kafka_producers import send_kafka_message
from src.shared.common_functions import decode_token, verify_response
from src.shared.config import settings
from src.shared.logger_setup import setup_logger
from src.shared.schemas import SessionDTO, AccessTokenUpdate, SessionSchema

logger = setup_logger(__name__)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Create access token
    :param data: Payload data
    :param expires_delta: Expiration time
    :return: str: JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(seconds=settings.access_token_expire_seconds,
                                            minutes=settings.access_token_expire_minutes,
                                            hours=settings.access_token_expire_hours)
    to_encode.update({"exp": expire.timestamp(), "iat": int(datetime.now().timestamp())})
    logger.info(
        f"Access token created for user: {data['sub']} with expiration: {datetime.fromtimestamp(expire.timestamp())}")
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    logger.info(f"Access token: {encoded_jwt}")
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Create refresh token
    :param data: Payload data
    :param expires_delta: Expiration time
    :return: str: JWT token
    """
    to_encode: dict[str, any] = deepcopy(data)
    logger.info(to_encode)
    logger.info(data)
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire.timestamp()})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_refresh, algorithm=settings.jwt_algorithm)
    logger.info(f"Refresh token created for user: {data['sub']} {encoded_jwt}")
    return encoded_jwt


def create_new_token(email: str, is_refresh: bool = False):
    """
    Create new access or refresh token
    :param email: User email for sub header
    :param is_refresh: True if refresh token needs to be created
    :return: str: JWT token
    """
    data = {"iss": "auth-service", "sub": email, "jti": str(uuid.uuid4())}
    return create_refresh_token(data=data) if is_refresh else create_access_token(data=data)


def is_about_to_expire(exp_time: datetime, threshold: int = settings.about_to_expire_seconds) -> bool:
    """
    Check if token is about to expire
    :param exp_time:
    :param threshold:
    :return: bool
    """
    time_left = (exp_time - datetime.now()).total_seconds()
    logger.info(f"check: time left until token expiration: {time_left} seconds")
    return time_left < threshold


async def verify_and_refresh_access_token(token: str) -> str | None:
    """
    Verify and refresh access token
    :param token: Access token
    :return:str | None: New access token or None if error
    """
    try:

        # Check if the token is a decoded JWT
        payload: dict[str, any] | None = decode_token(token)
        if not payload:
            logger.error("Token verification failed")
            return None

        # Check if we have session for token
        response = await get_session_by_token(token)
        error = verify_response(response)
        if error:
            logger.error(f"Cannot find session with token {token}")
            return None
        session = SessionDTO(**response.json())
        logger.info(f"Token verification succeeded: {session}")
        # Check token exp time
        exp_time: datetime = datetime.fromtimestamp(payload.get("exp"))
        logger.info(f"Token expires at: {exp_time}")
        about_to_expire: bool = is_about_to_expire(exp_time)

        if about_to_expire or exp_time <= datetime.now():
            logger.warning("Token is about to expire" if about_to_expire else f"Token expired at: {exp_time}")
            # Check if we have refresh token
            if session.refresh_token:
                # Update session with new access token
                logger.info("Refreshing token using refresh token")
                new_token: str = await refresh_access_token(session.refresh_token)
                # Check if we have new token and update session
                if not new_token:
                    logger.error("Failed to refresh token")
                    return None
                logger.info("Token refreshed successfully")
                return new_token
            else:
                # Create new access token without refsrh token and update session
                logger.info("Creating new access token")
                new_access_token = create_new_token(payload['sub'])
                if not new_access_token:
                    logger.error("Failed to create new access token")
                    return None
                response = await update_session_token(session.session_id,
                                     AccessTokenUpdate(old_access_token=token, new_access_token=new_access_token))
                error = verify_response(response)
                if error:
                    logger.error("Failed to verify new access token")
                    return None
                return new_access_token
        logger.info("Token is valid")
        return token
    except JWTError as e:
        logger.warning(f"JWTError: {e}")
        return None


async def refresh_access_token(refresh_token: str):
    """
    Refresh access token using refresh token
    :param refresh_token: Refresh token
    :return: str | None: New access token or None if error
    """
    try:
        # Decode token and check it
        payload = decode_token(refresh_token, is_refresh=True)
        if not refresh_token:
            logger.error("Refresh token is not valid or has expired")
            return None
        if not payload:
            logger.error("Invalid refresh token")
            return None
        email = payload.get("sub")
        if not email:
            logger.error("No email in refresh token payload")
            return None

        # Get session by refresh token
        response = await get_session_by_token(refresh_token, token_type="refresh_token")
        error = verify_response(response)
        if error:
            logger.error("Failed to verify new access token")
            return None
        session = SessionDTO(**response.json())

        # Create new access token
        new_access_token = create_new_token(email)
        if not new_access_token:
            logger.error("Failed to create new access token")
            return None

        #If refresh token is expired, create new refresh token session
        exp_time: datetime = datetime.fromtimestamp(payload.get("exp"))
        logger.info(f"Token expires at: {exp_time}")
        about_to_expire: bool = is_about_to_expire(exp_time)

        if about_to_expire or exp_time <= datetime.now():
            logger.warning("Refresh token is about to expire" if about_to_expire else f"Refresh token expired at: {exp_time}")
            # Create new refresh token
            new_refresh_token = create_new_token(email, is_refresh=True)
            if not new_refresh_token:
                logger.error("Failed to create new refresh token")
                return None
            # Update session with new refresh token
            response = await create_session(
                SessionSchema(
                    user_id=session.user_id,
                    access_token=new_access_token,
                    refresh_token=new_refresh_token,
                    device=session.device,
                    ip_address=session.ip_address)
            )

        # Otherwise Update session token
        else: response = await update_session_token(session.session_id, AccessTokenUpdate(old_access_token=session.access_token,
                                                                      new_access_token=new_access_token))
        error = verify_response(response)
        if error:
            logger.error("Failed to verify new access token")
            return None
        return new_access_token

    except JWTError as e:
        logger.warning(f"refresh_access_token - JWT Error: {e}")
        return None


async def send_email_signal(access_token:str, user_email:str, message_type:str = "register_email"):
    message = await send_kafka_message({"message_type": message_type,"token": access_token, "email": user_email})

    if not message:
        logger.warning(f"Failed to send {message_type} email")
        return None

    logger.info(f"Send {message_type} email signal sent for {user_email}")
    return message