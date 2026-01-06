import json
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from uuid import uuid4

from config.connection_manager import manager
from app.chat.application.use_case.get_chat_history_use_case import GetChatHistoryUseCase
from app.chat.application.use_case.get_my_chat_rooms_use_case import GetMyChatRoomsUseCase
from app.chat.application.use_case.mark_chat_room_as_read_use_case import MarkChatRoomAsReadUseCase
from app.chat.application.use_case.leave_chat_room_use_case import LeaveChatRoomUseCase
from app.chat.application.use_case.report_user_use_case import ReportUserUseCase
from app.chat.application.use_case.rate_user_use_case import RateUserUseCase
from app.chat.application.port.chat_message_repository_port import ChatMessageRepositoryPort
from app.chat.application.port.chat_room_repository_port import ChatRoomRepositoryPort
from app.chat.application.port.report_repository_port import ReportRepositoryPort
from app.chat.application.port.rating_repository_port import RatingRepositoryPort
from app.chat.infrastructure.repository.mysql_chat_message_repository import MySQLChatMessageRepository
from app.chat.infrastructure.repository.mysql_chat_room_repository import MySQLChatRoomRepository
from app.chat.infrastructure.repository.mysql_report_repository import MySQLReportRepository
from app.chat.infrastructure.repository.mysql_rating_repository import MySQLRatingRepository
from app.chat.domain.report import ReportReason
from app.chat.application.dto.rate_user_request import RateUserRequest
from config.database import get_db

chat_router = APIRouter()


def get_chat_message_repository(db: Session = Depends(get_db)) -> ChatMessageRepositoryPort:
    """ChatMessage Repository 의존성 주입"""
    return MySQLChatMessageRepository(db)


def get_chat_room_repository(db: Session = Depends(get_db)) -> ChatRoomRepositoryPort:
    """ChatRoom Repository 의존성 주입"""
    return MySQLChatRoomRepository(db)


def get_report_repository(db: Session = Depends(get_db)) -> ReportRepositoryPort:
    """Report Repository 의존성 주입"""
    return MySQLReportRepository(db)


def get_rating_repository(db: Session = Depends(get_db)) -> RatingRepositoryPort:
    """Rating Repository 의존성 주입"""
    return MySQLRatingRepository(db)


class ChatMessageResponse(BaseModel):
    """채팅 메시지 응답 DTO"""
    id: str
    room_id: str
    sender_id: str
    content: str
    created_at: datetime


class ChatHistoryResponse(BaseModel):
    """채팅 기록 응답 DTO"""
    messages: list[ChatMessageResponse]


class ChatRoomPreviewResponse(BaseModel):
    """채팅방 미리보기 응답 DTO"""
    id: str
    user1_id: str
    user2_id: str
    created_at: datetime
    status: str = "active"
    latest_message: Optional[ChatMessageResponse] = None
    unread_count: int = 0


class MyChatRoomsResponse(BaseModel):
    """내 채팅방 목록 응답 DTO"""
    rooms: list[ChatRoomPreviewResponse]


@chat_router.get("/chat/{room_id}/messages", response_model=ChatHistoryResponse)
def get_chat_history(
    room_id: str,
    repository: ChatMessageRepositoryPort = Depends(get_chat_message_repository)
):
    """
    채팅방의 메시지 기록을 조회한다.

    - room_id: 채팅방 ID
    - 반환: 시간순으로 정렬된 메시지 목록
    """
    use_case = GetChatHistoryUseCase(repository)
    messages = use_case.execute(room_id)

    message_responses = [
        ChatMessageResponse(
            id=msg.id,
            room_id=msg.room_id,
            sender_id=msg.sender_id,
            content=msg.content,
            created_at=msg.created_at
        )
        for msg in messages
    ]

    return ChatHistoryResponse(messages=message_responses)


@chat_router.get("/chat/rooms/my", response_model=MyChatRoomsResponse)
def get_my_chat_rooms(
    user_id: str,
    room_repository: ChatRoomRepositoryPort = Depends(get_chat_room_repository),
    message_repository: ChatMessageRepositoryPort = Depends(get_chat_message_repository)
):
    """
    사용자의 채팅방 목록을 조회한다.

    - user_id: 사용자 ID
    - 반환: 최신 메시지 미리보기와 읽지 않은 메시지 수를 포함한 채팅방 목록
    """
    use_case = GetMyChatRoomsUseCase(room_repository, message_repository)
    room_previews = use_case.execute(user_id)

    room_responses = []
    for preview in room_previews:
        latest_message_response = None
        if preview.latest_message:
            latest_message_response = ChatMessageResponse(
                id=preview.latest_message.id,
                room_id=preview.latest_message.room_id,
                sender_id=preview.latest_message.sender_id,
                content=preview.latest_message.content,
                created_at=preview.latest_message.created_at
            )

        room_response = ChatRoomPreviewResponse(
            id=preview.id,
            user1_id=preview.user1_id,
            user2_id=preview.user2_id,
            created_at=preview.created_at,
            status=preview.status,
            latest_message=latest_message_response,
            unread_count=preview.unread_count
        )
        room_responses.append(room_response)

    return MyChatRoomsResponse(rooms=room_responses)


@chat_router.post("/chat/{room_id}/read")
def mark_room_as_read(
    room_id: str,
    user_id: str,
    room_repository: ChatRoomRepositoryPort = Depends(get_chat_room_repository)
):
    """
    채팅방의 메시지를 읽음 처리한다.

    - room_id: 채팅방 ID
    - user_id: 읽음 처리할 사용자 ID (query parameter)
    """
    use_case = MarkChatRoomAsReadUseCase(room_repository)
    use_case.execute(room_id, user_id)

    return {"status": "success", "message": "채팅방이 읽음 처리되었습니다"}


async def _notify_partner_left(room_id: str, left_user_id: str):
    """상대방에게 파트너가 나갔음을 알린다"""
    message = json.dumps({
        "type": "partner_left",
        "room_id": room_id,
        "user_id": left_user_id
    })
    await manager.broadcast(message, room_id)


@chat_router.post("/chat/{room_id}/leave")
async def leave_chat_room(
    room_id: str,
    user_id: str,
    background_tasks: BackgroundTasks,
    room_repository: ChatRoomRepositoryPort = Depends(get_chat_room_repository)
):
    """
    채팅방을 나간다.

    - room_id: 채팅방 ID
    - user_id: 나가는 사용자 ID (query parameter)
    """
    use_case = LeaveChatRoomUseCase(room_repository)
    use_case.execute(room_id, user_id)

    # WebSocket으로 상대방에게 알림
    await _notify_partner_left(room_id, user_id)

    return {"status": "success", "message": "채팅방을 나갔습니다"}


class ReportMessageRequest(BaseModel):
    """메시지 신고 요청 DTO"""
    reporter_id: str
    reasons: list[str]  # ABUSE, HARASSMENT, SPAM, OTHER


class ReportMessageResponse(BaseModel):
    """메시지 신고 응답 DTO"""
    report_id: str
    status: str
    message: str


@chat_router.post("/chat/messages/{message_id}/report", response_model=ReportMessageResponse)
def report_message(
    message_id: str,
    request: ReportMessageRequest,
    report_repository: ReportRepositoryPort = Depends(get_report_repository),
    room_repository: ChatRoomRepositoryPort = Depends(get_chat_room_repository),
    message_repository: ChatMessageRepositoryPort = Depends(get_chat_message_repository)
):
    """
    메시지를 신고한다.

    - message_id: 신고할 메시지 ID
    - reporter_id: 신고자 ID
    - reasons: 신고 사유 목록 (ABUSE, HARASSMENT, SPAM, OTHER)
    """
    # 문자열을 ReportReason enum으로 변환
    reason_enums = [ReportReason(r) for r in request.reasons]

    use_case = ReportUserUseCase(report_repository, room_repository, message_repository)
    report_id = use_case.execute(request.reporter_id, message_id, reason_enums)

    return ReportMessageResponse(
        report_id=report_id,
        status="success",
        message="신고가 접수되었습니다"
    )


class RateUserApiRequest(BaseModel):
    rater_id: str
    rated_user_id: str
    score: int
    feedback: Optional[str] = None


@chat_router.post("/chat/{room_id}/rate")
def rate_user_in_chat(
    room_id: str,
    request: RateUserApiRequest,
    rating_repo: RatingRepositoryPort = Depends(get_rating_repository),
    room_repo: ChatRoomRepositoryPort = Depends(get_chat_room_repository),
):
    """
    채팅방의 다른 사용자를 평가한다.

    - room_id: 채팅방 ID
    - rater_id: 평가자 ID
    - rated_user_id: 피평가자 ID
    - score: 1-5점
    - feedback: 선택적 피드백
    """
    # Check if both users are actually in the room
    room = room_repo.find_by_id(room_id)
    if not room or not {request.rater_id, request.rated_user_id}.issubset({room.user1_id, room.user2_id}):
        raise HTTPException(status_code=404, detail="채팅방을 찾을 수 없거나 사용자가 채팅방에 속해있지 않습니다.")

    if request.rater_id == request.rated_user_id:
        raise HTTPException(status_code=400, detail="자기 자신을 평가할 수 없습니다.")

    use_case = RateUserUseCase(rating_repo=rating_repo, uuid_generator=uuid4)

    use_case_request = RateUserRequest(
        rater_id=request.rater_id,
        rated_user_id=request.rated_user_id,
        room_id=room_id,
        score=request.score,
        feedback=request.feedback
    )

    try:
        use_case.execute(use_case_request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"status": "success", "message": "평가가 성공적으로 제출되었습니다."}
