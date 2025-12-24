import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from app.match.adapter.output.chat.chat_client_adapter import ChatClientAdapter


@pytest.mark.asyncio
async def test_chat_adapter_calls_usecase_correctly():
    """
    Match Payload가 Chat UseCase 인자로 올바르게 변환되어 전달되는지 검증
    """
    # Given
    payload = {
        "roomId": "room_123",
        "users": [
            {"userId": "user_a", "mbti": "INFP"},
            {"userId": "user_b", "mbti": "ENFJ"}
        ],
        "timestamp": datetime.now().isoformat()
    }

    # Chat 도메인과 DB 세션을 Mocking
    with patch("app.match.adapter.output.chat.chat_client_adapter.get_db_session") as mock_get_db, \
            patch("app.match.adapter.output.chat.chat_client_adapter.MySQLChatRoomRepository") as mock_repo_cls, \
            patch("app.match.adapter.output.chat.chat_client_adapter.CreateChatRoomUseCase") as mock_usecase_cls:
        # Mock 설정
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        mock_usecase_instance = MagicMock()
        mock_usecase_cls.return_value = mock_usecase_instance

        adapter = ChatClientAdapter()

        # When
        result = await adapter.create_chat_room(payload)

        # Then
        assert result is True

        # UseCase가 올바른 인자(분해된 users)로 호출되었는지 확인
        mock_usecase_instance.execute.assert_called_once()
        call_args = mock_usecase_instance.execute.call_args[1]  # keyword arguments 확인

        assert call_args["room_id"] == "room_123"
        assert call_args["user1_id"] == "user_a"
        assert call_args["user2_id"] == "user_b"
        # timestamp는 datetime 객체로 변환되었어야 함
        assert isinstance(call_args["timestamp"], datetime)

        # DB 세션이 닫혔는지 확인
        mock_db.close.assert_called_once()