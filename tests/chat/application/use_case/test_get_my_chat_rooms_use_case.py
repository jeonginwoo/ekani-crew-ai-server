from datetime import datetime, timedelta
import pytest

from app.chat.domain.chat_room import ChatRoom
from app.chat.domain.chat_message import ChatMessage
from app.chat.application.use_case.get_my_chat_rooms_use_case import GetMyChatRoomsUseCase
from tests.chat.fixtures.fake_chat_room_repository import FakeChatRoomRepository
from tests.chat.fixtures.fake_chat_message_repository import FakeChatMessageRepository


class TestGetMyChatRoomsUseCase:
    """GetMyChatRoomsUseCase 테스트"""

    def test_get_my_chat_rooms_returns_rooms_where_user_is_participant(self):
        """사용자가 참여한 채팅방 목록을 반환한다"""
        # Given: 3개의 채팅방이 있고, user-1은 2개 방에 참여
        room_repository = FakeChatRoomRepository()
        message_repository = FakeChatMessageRepository()

        room1 = ChatRoom(
            id="room-1",
            user1_id="user-1",
            user2_id="user-2",
            created_at=datetime.now() - timedelta(days=2)
        )
        room2 = ChatRoom(
            id="room-2",
            user1_id="user-3",
            user2_id="user-1",
            created_at=datetime.now() - timedelta(days=1)
        )
        room3 = ChatRoom(
            id="room-3",
            user1_id="user-3",
            user2_id="user-4",
            created_at=datetime.now()
        )

        room_repository.save(room1)
        room_repository.save(room2)
        room_repository.save(room3)

        use_case = GetMyChatRoomsUseCase(room_repository, message_repository)

        # When: user-1의 채팅방 목록을 조회한다
        rooms = use_case.execute("user-1")

        # Then: user-1이 참여한 2개의 방이 반환된다
        assert len(rooms) == 2
        room_ids = [room.id for room in rooms]
        assert "room-1" in room_ids
        assert "room-2" in room_ids
        assert "room-3" not in room_ids

    def test_get_my_chat_rooms_includes_most_recent_message(self):
        """각 채팅방의 최신 메시지를 포함한다"""
        # Given: 채팅방과 여러 메시지가 있다
        room_repository = FakeChatRoomRepository()
        message_repository = FakeChatMessageRepository()

        room1 = ChatRoom(
            id="room-1",
            user1_id="user-1",
            user2_id="user-2",
            created_at=datetime.now() - timedelta(days=1)
        )
        room_repository.save(room1)

        # room-1에 3개의 메시지 (시간순)
        msg1 = ChatMessage(
            id="msg-1",
            room_id="room-1",
            sender_id="user-1",
            content="First message",
            created_at=datetime.now() - timedelta(hours=3)
        )
        msg2 = ChatMessage(
            id="msg-2",
            room_id="room-1",
            sender_id="user-2",
            content="Second message",
            created_at=datetime.now() - timedelta(hours=2)
        )
        msg3 = ChatMessage(
            id="msg-3",
            room_id="room-1",
            sender_id="user-1",
            content="Most recent message",
            created_at=datetime.now() - timedelta(hours=1)
        )

        message_repository.save(msg1)
        message_repository.save(msg2)
        message_repository.save(msg3)

        use_case = GetMyChatRoomsUseCase(room_repository, message_repository)

        # When: user-1의 채팅방 목록을 조회한다
        rooms = use_case.execute("user-1")

        # Then: 최신 메시지가 포함된다
        assert len(rooms) == 1
        assert rooms[0].latest_message is not None
        assert rooms[0].latest_message.id == "msg-3"
        assert rooms[0].latest_message.content == "Most recent message"

    def test_get_my_chat_rooms_includes_unread_count(self):
        """각 채팅방의 읽지 않은 메시지 수를 포함한다"""
        # Given: 채팅방과 읽지 않은 메시지가 있다
        room_repository = FakeChatRoomRepository()
        message_repository = FakeChatMessageRepository()

        room1 = ChatRoom(
            id="room-1",
            user1_id="user-1",
            user2_id="user-2",
            created_at=datetime.now() - timedelta(days=1)
        )
        room_repository.save(room1)

        # user-2가 보낸 메시지 3개 (user-1이 읽지 않음)
        msg1 = ChatMessage(
            id="msg-1",
            room_id="room-1",
            sender_id="user-2",
            content="Message 1",
            created_at=datetime.now() - timedelta(hours=3)
        )
        msg2 = ChatMessage(
            id="msg-2",
            room_id="room-1",
            sender_id="user-2",
            content="Message 2",
            created_at=datetime.now() - timedelta(hours=2)
        )
        # user-1이 보낸 메시지 (읽지 않은 메시지에 포함 안 됨)
        msg3 = ChatMessage(
            id="msg-3",
            room_id="room-1",
            sender_id="user-1",
            content="Message 3",
            created_at=datetime.now() - timedelta(hours=1)
        )

        message_repository.save(msg1)
        message_repository.save(msg2)
        message_repository.save(msg3)

        use_case = GetMyChatRoomsUseCase(room_repository, message_repository)

        # When: user-1의 채팅방 목록을 조회한다
        rooms = use_case.execute("user-1")

        # Then: 읽지 않은 메시지 수가 2개다 (user-2가 보낸 메시지만)
        assert len(rooms) == 1
        assert rooms[0].unread_count == 2

    def test_get_my_chat_rooms_returns_empty_list_for_user_with_no_rooms(self):
        """채팅방이 없는 사용자는 빈 리스트를 반환한다"""
        # Given: 빈 저장소
        room_repository = FakeChatRoomRepository()
        message_repository = FakeChatMessageRepository()
        use_case = GetMyChatRoomsUseCase(room_repository, message_repository)

        # When: 채팅방이 없는 사용자의 목록을 조회한다
        rooms = use_case.execute("user-no-rooms")

        # Then: 빈 리스트가 반환된다
        assert rooms == []
