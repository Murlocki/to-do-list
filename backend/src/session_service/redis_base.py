import redis
import redis.asyncio as aioredis

from src.shared.config import settings


def get_redis_client():
    return aioredis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        db=settings.redis_db,
        decode_responses=True,

    )


redis_client = get_redis_client()


def check_redis_connection():
    try:
        response = redis_client.ping()
        return response
    except redis.ConnectionError:
        return False
