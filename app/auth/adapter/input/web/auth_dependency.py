from fastapi import Header, Cookie, HTTPException, status

from app.auth.infrastructure.repository.redis_session_repository import RedisSessionRepository
from config.redis import redis_client


async def get_current_user_id(
    authorization: str | None = Header(default=None),
    session_id_cookie: str | None = Cookie(default=None, alias="session_id"),
) -> str:
    """
    현재 요청의 user_id를 반환하는 의존성 (비동기).

    Authorization 헤더에서 Bearer 토큰(세션 ID)을 추출하고,
    Redis 세션 저장소에서 검증하여 user_id를 반환한다.
    """
    session_id = None

    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            session_id = parts[1]
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="올바른 인증 형식이 아닙니다",
            )

    # Authorization이 없으면 쿠키로 대체
    if session_id is None and session_id_cookie:
        session_id = session_id_cookie

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다",
        )

    # Redis 세션 저장소에서 검증 (비동기)
    session_repo = RedisSessionRepository(redis_client)
    session = await session_repo.find_by_session_id(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 세션입니다",
        )

    return session.user_id
