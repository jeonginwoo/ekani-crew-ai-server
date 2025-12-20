import redis.asyncio as aioredis

from app.auth.application.port.session_repository_port import SessionRepositoryPort
from app.auth.domain.session import Session


class RedisSessionRepository(SessionRepositoryPort):
    """Redis 기반 세션 저장소 (비동기)"""

    DEFAULT_TTL_SECONDS = 60 * 60 * 6  # 6시간

    def __init__(self, redis_client: aioredis.Redis, ttl_seconds: int | None = None):
        self._redis = redis_client
        self._ttl = ttl_seconds if ttl_seconds is not None else self.DEFAULT_TTL_SECONDS

    def _get_key(self, session_id: str) -> str:
        """Redis 키 생성"""
        return f"session:{session_id}"

    async def save(self, session: Session) -> None:
        """세션을 저장한다"""
        key = self._get_key(session.session_id)
        await self._redis.setex(key, self._ttl, session.user_id)

    async def find_by_session_id(self, session_id: str) -> Session | None:
        """session_id로 세션을 조회한다"""
        key = self._get_key(session_id)
        user_id = await self._redis.get(key)

        if user_id is None:
            return None

        return Session(session_id=session_id, user_id=user_id)

    async def delete(self, session_id: str) -> None:
        """세션을 삭제한다"""
        key = self._get_key(session_id)
        await self._redis.delete(key)