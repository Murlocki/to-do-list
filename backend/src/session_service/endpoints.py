from src.session_service.config import settings

GET_USERS = f"{settings.profile_service_url}/user"
CHECk_AUTH = f"{settings.auth_service_url}/auth/check_auth"