from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.chat.domain.chat_message import ChatMessage


@dataclass
class ChatRoomWithPreviewDTO:
    """채팅방 목록 조회용 DTO (최신 메시지 미리보기 및 읽지 않은 메시지 수 포함)"""
    id: str
    user1_id: str
    user2_id: str
    created_at: datetime
    latest_message: Optional[ChatMessage] = None
    unread_count: int = 0
