from app.chat.application.port.chat_message_repository_port import ChatMessageRepositoryPort
from app.chat.domain.chat_message import ChatMessage


class GetChatHistoryUseCase:
    """채팅 기록 조회 유스케이스"""

    def __init__(self, repository: ChatMessageRepositoryPort):
        self._repository = repository

    def execute(self, room_id: str) -> list[ChatMessage]:
        """채팅방의 메시지 기록을 시간순으로 조회한다"""
        return self._repository.find_by_room_id(room_id)
