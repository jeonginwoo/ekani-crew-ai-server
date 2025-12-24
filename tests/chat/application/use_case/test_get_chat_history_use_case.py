from datetime import datetime, timedelta
import pytest

from app.chat.domain.chat_message import ChatMessage
from app.chat.application.use_case.get_chat_history_use_case import GetChatHistoryUseCase
from tests.chat.fixtures.fake_chat_message_repository import FakeChatMessageRepository


class TestGetChatHistoryUseCase:
    """GetChatHistoryUseCase 테스트"""

    def test_get_chat_history_returns_messages_in_chronological_order(self):
        """채팅 메시지를 시간순으로 조회한다"""
        # Given: 3개의 메시지가 있는 채팅방
        repository = FakeChatMessageRepository()
        room_id = "room-123"

        # 시간 순서대로 저장 (나중에 저장된 것이 최신)
        msg1 = ChatMessage(
            id="msg-1",
            room_id=room_id,
            sender_id="user-1",
            content="First message",
            created_at=datetime.now() - timedelta(minutes=10)
        )
        msg2 = ChatMessage(
            id="msg-2",
            room_id=room_id,
            sender_id="user-2",
            content="Second message",
            created_at=datetime.now() - timedelta(minutes=5)
        )
        msg3 = ChatMessage(
            id="msg-3",
            room_id=room_id,
            sender_id="user-1",
            content="Third message",
            created_at=datetime.now()
        )

        repository.save(msg1)
        repository.save(msg2)
        repository.save(msg3)

        use_case = GetChatHistoryUseCase(repository)

        # When: 채팅 기록을 조회한다
        messages = use_case.execute(room_id)

        # Then: 메시지가 시간순으로 정렬되어 반환된다
        assert len(messages) == 3
        assert messages[0].id == "msg-1"
        assert messages[1].id == "msg-2"
        assert messages[2].id == "msg-3"
        assert messages[0].content == "First message"
        assert messages[1].content == "Second message"
        assert messages[2].content == "Third message"

    def test_get_chat_history_returns_empty_list_for_nonexistent_room(self):
        """존재하지 않는 채팅방은 빈 리스트를 반환한다"""
        # Given: 빈 저장소
        repository = FakeChatMessageRepository()
        use_case = GetChatHistoryUseCase(repository)

        # When: 존재하지 않는 채팅방의 기록을 조회한다
        messages = use_case.execute("nonexistent-room")

        # Then: 빈 리스트가 반환된다
        assert messages == []

    def test_get_chat_history_filters_by_room_id(self):
        """특정 채팅방의 메시지만 조회한다"""
        # Given: 두 개의 채팅방에 메시지가 있다
        repository = FakeChatMessageRepository()

        msg_room1 = ChatMessage(
            id="msg-1",
            room_id="room-1",
            sender_id="user-1",
            content="Message in room 1"
        )
        msg_room2 = ChatMessage(
            id="msg-2",
            room_id="room-2",
            sender_id="user-2",
            content="Message in room 2"
        )

        repository.save(msg_room1)
        repository.save(msg_room2)

        use_case = GetChatHistoryUseCase(repository)

        # When: room-1의 메시지만 조회한다
        messages = use_case.execute("room-1")

        # Then: room-1의 메시지만 반환된다
        assert len(messages) == 1
        assert messages[0].id == "msg-1"
        assert messages[0].room_id == "room-1"
