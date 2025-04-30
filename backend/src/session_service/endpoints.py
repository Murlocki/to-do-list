from src.shared.config import settings

GET_USERS = f"{settings.user_service_url}/user"
CHECK_AUTH = f"{settings.auth_service_url}/auth/check_auth"
FIND_USER_BY_EMAIL = f"{settings.user_service_url}/user/crud/search"