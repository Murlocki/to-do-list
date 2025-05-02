from httpx import Response
from jose import jwt, JWTError

from src.shared.config import settings
from src.shared.logger_setup import setup_logger

logger = setup_logger(__name__)


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


def verify_response(response: Response, waited_status_code: int = 200) -> dict[str, int | str] | None:
    """
    Verify response code
    :param response: Response to verify
    :param waited_status_code: Waited status code
    :return: Error if status code is not matched
    """
    if response.status_code != waited_status_code:
        try:
            detail = response.json().get("detail", "Unknown error")
        except Exception:
            detail = response.text or "Unknown error"
        logger.error(f"Response error: code - {response.status_code} detail - {detail}")
        return {"status_code": response.status_code, "detail": detail}
    logger.info(f"Verified response {response.json()} successfully")
    return None
