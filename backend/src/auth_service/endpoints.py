from src.auth_service.config import settings

CREATE_SESSION = f"{settings.session_service_url}/session/crud"
GET_SESSION_BY_TOKEN = f"{settings.session_service_url}/session/crud/search"
UPDATE_SESSION_TOKEN = f"{settings.session_service_url}/session/crud"
DELETE_SESSION = f"{settings.session_service_url}/session/crud"
CREATE_USER = f"{settings.user_service_url}/user/crud"
AUTHENTICATE_USER = f"{settings.user_service_url}/user/authenticate"