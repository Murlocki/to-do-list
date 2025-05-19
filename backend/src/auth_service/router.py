import os
import time
from datetime import datetime

from fastapi import HTTPException, status, APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.auth_service import auth_functions
from src.auth_service.auth_functions import verify_and_refresh_access_token, send_email_signal
from src.auth_service.external_functions import create_session, get_session_by_token, delete_session_by_id, create_user, \
    authenticate_user, find_user_by_email, update_user, delete_sessions_by_token, update_user_password, \
    get_user_sessions
from src.auth_service.schemas import UserCreate, AuthForm
from src.shared import logger_setup
from src.shared.common_functions import decode_token, verify_response
from src.shared.schemas import SessionSchema, AuthResponse, SessionDTO, UserAuthDTO, PasswordForm
from src.shared.schemas import TokenModelResponse
from src.shared.schemas import UserDTO

auth_router = APIRouter()
logger = logger_setup.setup_logger(__name__)
logger.info(f"""
Server start time (UTC): {datetime.now()}
Server timestamp: {int(time.time())}
System timezone: {time.tzname}
Environment timezone: {os.environ.get('TZ', 'Not set')}
""")

bearer = HTTPBearer()


@auth_router.post("/auth/register", response_model=UserDTO, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """
    Register a new user
    :param user_data: User data from create form
    :return: UserDTO object
    :raises HTTPException: With appropriate status code and detail
    """
    # 1. Создание пользователя
    response = await create_user(user=user_data)
    if error := verify_response(response, 201):
        logger.error(f"User creation failed: {error}")
        raise HTTPException(status_code=error["status_code"], detail=error["detail"])

    user = UserDTO(**response.json())
    logger.info(f"User {user.username} registered")

    # 2. Создание сессии
    register_token = auth_functions.create_new_token(user.email)
    response = await create_session(
        SessionSchema(
            user_id=user.id,
            access_token=register_token
        )
    )

    if error := verify_response(response, 201):
        logger.warning(f"Session creation failed: {error}")
        raise HTTPException(status_code=error["status_code"], detail=error["detail"])

    session_data = SessionDTO(**response.json())
    logger.info(f"Register session created: {session_data}")

    # 3. Отправка email (не критично для регистрации)
    try:
        if not await send_email_signal(register_token, user.email):
            logger.warning(f"Email not sent for user {user.username}")
    except Exception as e:
        logger.error(f"Email sending error: {str(e)}", exc_info=True)
        # Продолжаем работу, так как email не критичен

    return user

@auth_router.post("/auth/activate_account", status_code=status.HTTP_200_OK)
async def activate_account(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    """
    Activate a user
    :param credentials: header with token
    :return: Activated user's data
    """
    # Checking token
    token_verified = await check_auth(credentials)
    if not token_verified or not token_verified["token"]:
        logger.error(f"Invalid token for registed user with credentials {credentials}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    logger.info(f"Token verified: {token_verified['token']}")
    payload = decode_token(token_verified["token"])
    logger.info(f"Token decoded: {payload}")

    # Getting user by email
    response = await find_user_by_email(payload["sub"])
    error = verify_response(response,200)
    if error:
        logger.error(error)
        raise HTTPException(status_code=error["status_code"], detail=error["detail"])
    user = UserDTO(**response.json())
    logger.info(f"User {user.username} is found by email {payload['sub']}")

    # Activating user
    user.is_active = True
    response = await update_user(user, token_verified["token"],True)
    error = verify_response(response,200)
    if error:
        logger.error(error)
        raise HTTPException(status_code=error["status_code"], detail=error["detail"]["data"])
    logger.info(f"User {user.username} is updated by token {token_verified['token']}")

    # Delete activation session
    user_activated = AuthResponse.model_validate(response.json())
    response = await delete_sessions_by_token(user_activated.token, True)
    error = verify_response(response,200)
    if error:
        logger.error(error)
        logger.warning("Session may expired before deleting, but user is activated and session existence was checked at the beginning")
    logger.info(f"Successfully activated user {user.username}")
    return user_activated.data


@auth_router.post("/auth/login", response_model=TokenModelResponse, status_code=status.HTTP_200_OK)
async def login_user(auth_form: AuthForm):
    # Authenticate user
    response = await authenticate_user(UserAuthDTO(identifier=auth_form.identifier, password=auth_form.password))
    error = verify_response(response)
    if error:
        logger.error(error)
        raise HTTPException(status_code=error["status_code"], detail=error["detail"])
    user = UserDTO(**response.json())
    logger.info(f"User {user.username} is found")

    # Check if user is active
    if not user.is_active:
        logger.error(f"Could not login user {user.username} because it is inactive")

        response = await get_user_sessions(user.id)
        error = verify_response(response)
        if error:
            logger.error(error)
            raise HTTPException(status_code=error["status_code"], detail=error["detail"])
        sessions_data = response.json()
        sessions = [SessionDTO(**session) for session in sessions_data]
        if not sessions:
            logger.warning(f"User {user.username} has no sessions")
            new_register_token = auth_functions.create_new_token(user.email)
            response = await create_session(
                SessionSchema(
                    user_id=user.id,
                    access_token=new_register_token,
                    device=auth_form.device,
                    ip_address=auth_form.ip_address))
            error = verify_response(response, 201)
            if error:
                logger.error(error)
                raise HTTPException(status_code=error["status_code"], detail=error["detail"])
            message = await send_email_signal(new_register_token, user.email)
            if not message:
                logger.warning(f"Could not send email for user {user.username}, but he is registered")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Activate account")
    logger.info(f"User {user} logged in")

    # Create access tokens
    access_token = auth_functions.create_new_token(user.email)
    logger.info(f"User {user.username} logged in with access token {access_token}")
    # Create refresh token if remember_me is set
    refresh_token = auth_functions.create_new_token(user.email, is_refresh=True) if auth_form.remember_me else None
    response = await create_session(
        SessionSchema(
            user_id=user.id,
            access_token=access_token,
            refresh_token=refresh_token,
            device=auth_form.device,
            ip_address=auth_form.ip_address))
    error = verify_response(response, 201)
    if error:
        logger.error(error)
        raise HTTPException(status_code=error["status_code"], detail=error["detail"])
    logger.info(f"User logged in {'(rem mode)' if auth_form.remember_me else ''}: {user.email}")
    return TokenModelResponse(token=access_token).model_dump()


@auth_router.get("/auth/get_forgot_password_email/{email}", status_code=status.HTTP_200_OK)
async def get_forgot_password(email: str):
    """
    Create email for password reset link
    :param email: User's email'
    :return: Kafka message
    """
    # Find user by email
    response = await find_user_by_email(email)
    error = verify_response(response)
    if error:
        logger.error(error)
        raise HTTPException(status_code=error["status_code"], detail=error["detail"])
    user = UserDTO(**response.json())
    logger.info(f"User {user.username} is found by email {email}")

    recovery_token = auth_functions.create_new_token(email)
    logger.info(f"User {user.username}'s recovery token {recovery_token}")

    # Create recovery session
    response = await create_session(
        SessionSchema(
            user_id=user.id,
            access_token=recovery_token))
    error = verify_response(response, 201)
    if error:
        logger.error(error)
        raise HTTPException(status_code=error["status_code"], detail=error["detail"])
    logger.info(f"User {user.username} recovery session created")

    message = await send_email_signal(recovery_token, user.email, "recover_password")
    if not message:
        logger.warning(f"Could not send recovery message for user {user}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message not sent")
    logger.info(f"User {user.username} recovery message sent")
    return {"message": message}


@auth_router.post("/auth/forgot_password", status_code=status.HTTP_200_OK, response_model=AuthResponse)
async def forgot_password(new_password_form: PasswordForm, credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    """
    Reset user password
    :param new_password_form: Contains new user password
    :param credentials: Header with token
    :return: New token and UserDTO
    """
    token_verified = await check_auth(credentials)
    if not token_verified or not token_verified["token"]:
        logger.warning(f"Invalid token for forgot password")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    logger.info(f"Token verified: {token_verified['token']}")
    response = await update_user_password(new_password_form, token_verified["token"], True)
    error = verify_response(response)
    if error:
        logger.error(error)
        raise HTTPException(status_code=error["status_code"], detail=error["detail"])
    user = UserDTO(**response.json()["data"])
    logger.info(f"User {user.username} forgot password updated")
    return AuthResponse(data=user, token=token_verified["token"]).model_dump()


@auth_router.post("/auth/logout", status_code=status.HTTP_200_OK, response_model=AuthResponse)
async def logout_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    """
    Perform logout of user
    :param credentials: token
    :return: AuthResponse
    """
    # Check if token is valid
    token_verified = await check_auth(credentials)
    logger.info("Verified token {token_verified}")
    if not token_verified or not token_verified["token"]:
        logger.warning("Invalid token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "Invalid token"})
    token = token_verified["token"]
    logger.info(f"Valid Token: {token}")
    # Get session by token
    response = await get_session_by_token(token, token_type="access_token")
    error = verify_response(response)
    if error:
        logger.error(error)
        raise HTTPException(status_code=error["status_code"], detail=AuthResponse(token=token,data=error["detail"]).model_dump())
    session = SessionDTO(**response.json())
    logger.info(f"Found session {session}")
    # Delete session
    response = await delete_session_by_id(session.session_id, token, True)
    error = verify_response(response)
    if error:
        logger.error(error)
        raise HTTPException(status_code=error["status_code"], detail=error["detail"])
    logger.info(f"Session {session.session_id} deleted")
    return AuthResponse(data=response.json(), token=token).model_dump()


@auth_router.get("/auth/check_auth", response_model=TokenModelResponse)
async def check_auth(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    """
    Check if user is authenticated
    :param credentials: Carryind token in header
    :param db: Database session
    :return: Token data
    """
    token = credentials.credentials

    # Get token payload
    payload = decode_token(token)
    logger.info(f"Token decoded successfully {payload}")
    if not payload or not payload["sub"]:
        logger.warning("Invalid token")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "Invalid token",
                                                                           "token": None})

    # Get token user
    user = await find_user_by_email(email=payload["sub"])
    if not user:
        logger.warning("User not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "User is not found",
                                                                           "token": None})

    # Check token validity and refresh if needed
    token = await verify_and_refresh_access_token(token)
    if not token:
        logger.warning("Invalid new token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"message": "Invalid new token",
                                                                              "token": None})
    return {"token": token}
