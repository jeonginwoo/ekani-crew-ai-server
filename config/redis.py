import redis.asyncio as aioredis
from config.settings import get_settings

# 설정 가져오기
settings = get_settings()

# 비동기 Redis 클라이언트 생성
redis_client: aioredis.Redis = aioredis.from_url(
    settings.REDIS_URL,
    decode_responses=True
)


def get_redis() -> aioredis.Redis:
    """비동기 Redis 클라이언트 반환"""
    return redis_client