from src.shared.config import settings

CREATE_SESSION = f"{settings.session_service_url}/session/crud"
GET_SESSION_BY_TOKEN = f"{settings.session_service_url}/session/crud/search"
UPDATE_SESSION_TOKEN = f"{settings.session_service_url}/session/crud"
DELETE_SESSION = f"{settings.session_service_url}/session/crud/me"
DELETE_SESSION_BY_TOKEN = f"{settings.session_service_url}/session/crud/me"
GET_USER_SESSIONS = f"{settings.session_service_url}/session/crud/user"
CREATE_USER = f"{settings.user_service_url}/user/crud"
AUTHENTICATE_USER = (f"{settings.user_service_url}/user/authenticate")
FIND_USER_BY_EMAIL = f"{settings.user_service_url}/user/crud/search"
UPDATE_USER = f"{settings.user_service_url}/user/me/account"
UPDATE_USER_PASSWORD = f"{settings.user_service_url}/user/me/password"
