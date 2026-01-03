from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.match.adapter.input.web.request.match_cancel_request import MatchCancelRequest
from app.shared.vo.mbti import MBTI
from app.match.adapter.input.web.request.match_request import MatchRequest
from app.match.application.usecase.match_usecase import MatchUseCase
from config.database import get_db

# Dependency Imports
from app.match.application.port.output.match_queue_port import MatchQueuePort
from app.match.adapter.output.persistence.redis_match_queue_adapter import RedisMatchQueueAdapter
from app.match.application.port.output.chat_room_port import ChatRoomPort
from app.match.adapter.output.chat.chat_client_adapter import ChatClientAdapter
from app.user.application.port.block_repository_port import BlockRepositoryPort
from app.user.infrastructure.repository.mysql_block_repository import MySQLBlockRepository
from app.match.application.port.output.match_state_port import MatchStatePort
from app.match.adapter.output.persistence.redis_match_state_adapter import RedisMatchStateAdapter
from app.match.application.port.output.match_notification_port import MatchNotificationPort
from app.match.adapter.output.notification.websocket_match_notification_adapter import WebSocketMatchNotificationAdapter
from config.redis import get_redis
from config.connection_manager import manager as connection_manager


match_router = APIRouter()


# Provider functions for dependencies
def get_match_queue_port() -> MatchQueuePort:
    return RedisMatchQueueAdapter(get_redis())

def get_chat_room_port() -> ChatRoomPort:
    return ChatClientAdapter()

def get_block_repository(db: Session = Depends(get_db)) -> BlockRepositoryPort:
    return MySQLBlockRepository(db)

def get_match_state_port() -> MatchStatePort:
    return RedisMatchStateAdapter(get_redis())

def get_match_notification_port() -> MatchNotificationPort:
    return WebSocketMatchNotificationAdapter(connection_manager)

def get_match_use_case(
    match_queue_port: MatchQueuePort = Depends(get_match_queue_port),
    chat_room_port: ChatRoomPort = Depends(get_chat_room_port),
    block_repository: BlockRepositoryPort = Depends(get_block_repository),
    match_state_port: MatchStatePort = Depends(get_match_state_port),
    match_notification_port: MatchNotificationPort = Depends(get_match_notification_port)
) -> MatchUseCase:
    return MatchUseCase(
        match_queue_port=match_queue_port,
        chat_room_port=chat_room_port,
        block_repository=block_repository,
        match_state_port=match_state_port,
        match_notification_port=match_notification_port
    )


@match_router.post("/request")
async def request_match(
    request: MatchRequest,
    usecase: MatchUseCase = Depends(get_match_use_case)
):
    """
    매칭 대기열에 유저를 등록합니다.
    """
    try:
        mbti_enum = MBTI(request.mbti.upper())
        result = await usecase.request_match(
            user_id=request.user_id,
            mbti=mbti_enum,
            level=request.level
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@match_router.post("/cancel")
async def cancel_match(
    request: MatchCancelRequest,
    usecase: MatchUseCase = Depends(get_match_use_case)
):
    """
    매칭 대기열에서 유저를 삭제(취소)합니다.
    """
    try:
        mbti_enum = MBTI(request.mbti.upper())
        result = await usecase.cancel_match(request.user_id, mbti_enum)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@match_router.get("/queue/{mbti}")
async def get_queue_status(
    mbti: str,
    usecase: MatchUseCase = Depends(get_match_use_case)
):
    """
    (테스트용) 특정 MBTI 대기열의 현재 대기 인원수를 확인합니다.
    """
    try:
        mbti_enum = MBTI(mbti.upper())
        count = await usecase.get_waiting_count(mbti_enum)
        return {
            "mbti": mbti.upper(),
            "waiting_count": count
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="유효하지 않은 MBTI입니다.")