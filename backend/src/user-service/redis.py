import redis
from datetime import datetime

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def check_redis_connection():
    try:
        response = r.ping()
        return response
    except redis.ConnectionError:
        return False

