import redis.asyncio as aioredis

from src.shared.config import settings
from src.shared.logger_setup import setup_logger

logger = setup_logger(__name__)



async def listen_expirations():
    redis_client = aioredis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        db=settings.redis_db,
        decode_responses=True,
    )

    # Включаем события истечения ключей
    await redis_client.config_set("notify-keyspace-events", "Ex")

    pubsub = redis_client.pubsub()
    await pubsub.psubscribe("__keyevent@0__:expired")

    logger.info("Subscribed to key expiration events")

    async for message in pubsub.listen():
        try:
            if message["type"] != "pmessage":
                continue

            session_key = message["data"]
            logger.info(f"Expired key detected: {session_key}")

            if not session_key.startswith("session:"):
                continue

            # Удаление сессии из всех множеств user:{user_id}:sessions
            async for key in redis_client.scan_iter(match="user:*:sessions"):
                removed = await redis_client.srem(key, session_key.split(":")[1])
                if removed:
                    logger.info(f"Removed expired session {session_key} from {key}")

        except Exception as e:
            logger.error("Error handling expiration: %s", e, exc_info=True)
