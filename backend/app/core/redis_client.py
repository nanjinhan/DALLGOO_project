import redis

from app.core.config import settings

# decode_responses=True → 값을 str로 받음(bytes 아님)
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
