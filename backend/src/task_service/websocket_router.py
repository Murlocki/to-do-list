from datetime import datetime

from src.shared.common_functions import verify_response
from src.shared.logger_setup import setup_logger
from src.shared.schemas import SessionDTO
from src.task_service.external_functions import get_session_by_token, check_auth_from_external_service
from src.task_service.main import sio  # Импортируем созданный экземпляр sio

# Логгер для этого модуля
logger = setup_logger(__name__)



@sio.event
async def connect(sid, environ):
    try:
        logger.info(f"Client connecting: {sid}")
        # Send welcome message to the client
        await sio.emit('welcome', {
            'message': 'Connection established!',
            'sid': sid,
            'timestamp': datetime.now().isoformat()
        }, to=sid)
        logger.info(f"Client connected successfully: {sid}")

        # Check authorization token
        token = environ.get('HTTP_AUTHORIZATION').split(' ')[1]
        if not token:
            logger.error(f"Authorization token missing for {sid}")
            await sio.disconnect(sid)
            return
        logger.info(f"Authorization token: {token}")
        verify_result = await check_auth_from_external_service(token)
        logger.info(f"Verify result {verify_result}")
        if not verify_result or not verify_result["token"]:
            await sio.disconnect(sid)
            return

        # Get user session with the token
        response = await get_session_by_token(verify_result["token"])
        error = verify_response(response)
        if error:
            logger.error(f"Error finding session by token: {error}")
            await sio.disconnect(sid)
            return
        logger.info(f"Session response: {response.json()}")
        # Add user to his session room
        user_id = SessionDTO(**response.json()).user_id
        await sio.save_session(sid, {"user_id": user_id})
        await sio.enter_room(sid, f"user_{user_id}")
        logger.info(f"Session session id {user_id}")
    except Exception as e:
        logger.error(f"Connection error for {sid}: {str(e)}")
        raise


@sio.event
async def disconnect(sid):
    logger.info(f"Client disconnecting: {sid}")
    # Remove user session from redis
    user_id = await sio.get_session(sid)
    await sio.leave_room(sid, f"user_{user_id}")
    await sio.disconnect(sid)
    logger.info(f"Client disconnected: {sid}")



@sio.event
async def message(sid, data):
    logger.info(f"Message from {sid}: {data}")
    await sio.emit("response", {"data": "Message received!"}, to=sid)

@sio.event
async def task_remind(sid, data):
    """
    Обработка события task_remind
    :param sid: Идентификатор клиента
    :param data: Данные события
    """
    logger.info(f"Task remind event from {sid}: {data}")
    # Отправляем уведомление пользователю
    await sio.emit("task_remind", data, to=sid)