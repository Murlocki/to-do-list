from src.shared.config import settings

CHECK_AUTH = f"{settings.auth_service_url}/auth/check_auth"
FIND_USER_BY_EMAIL = f"{settings.user_service_url}/user/crud/search"
GET_SESSION_BY_TOKEN = f"{settings.session_service_url}/session/crud/search"