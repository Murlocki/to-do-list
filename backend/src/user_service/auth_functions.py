import re

from passlib.context import CryptContext

from src.shared.logger_setup import setup_logger

logger = setup_logger(__name__)
def validate_password(password: str) -> bool:
    return re.search("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*=])[A-Za-z\d!@#$%^&*=]{8,}$", password) is not None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    logger.info(f"{pwd_context.hash(plain_password)}, {hashed_password}")
    return pwd_context.verify(plain_password, hashed_password)
