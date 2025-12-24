from fastapi import Cookie, HTTPException, status

from app.auth.infrastructure.repository.redis_session_repository import RedisSessionRepository
from config.redis import redis_client


async def get_current_user_id(
    session_id: str | None = Cookie(default=None, alias="session_id"),
) -> str:
    """
    현재 요청의 user_id를 반환하는 의존성 (비동기).

    session_id 쿠키에서 세션 ID를 추출하고,
    Redis 세션 저장소에서 검증하여 user_id를 반환한다.
    """
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다",
        )

    session_repo = RedisSessionRepository(redis_client)
    session = await session_repo.find_by_session_id(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 세션입니다",
        )

    return session.user_id
