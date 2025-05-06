from src.shared.config import settings
CHECK_AUTH = f"{settings.auth_service_url}/auth/check_auth"
DELETE_USER_SESSIONS = f"{settings.session_service_url}/session/crud/me"
