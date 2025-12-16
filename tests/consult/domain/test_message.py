import pytest
from datetime import datetime

from app.consult.domain.message import Message


class TestMessage:
    """Message 도메인 테스트"""

    def test_message_creates_with_required_fields(self):
        """Message는 role, content로 생성된다"""
        message = Message(role="user", content="안녕하세요")

        assert message.role == "user"
        assert message.content == "안녕하세요"
        assert message.timestamp is not None

    def test_message_creates_with_custom_timestamp(self):
        """Message는 timestamp를 지정할 수 있다"""
        custom_time = datetime(2024, 1, 1, 12, 0, 0)
        message = Message(role="assistant", content="반갑습니다", timestamp=custom_time)

        assert message.timestamp == custom_time

    def test_message_role_must_be_user_or_assistant(self):
        """Message role은 user 또는 assistant만 허용된다"""
        with pytest.raises(ValueError, match="role은 'user' 또는 'assistant'"):
            Message(role="invalid", content="테스트")

    def test_message_content_cannot_be_empty(self):
        """Message content는 비어있을 수 없다"""
        with pytest.raises(ValueError, match="content는 비어있을 수 없습니다"):
            Message(role="user", content="")

    def test_message_content_cannot_be_whitespace_only(self):
        """Message content는 공백만 있을 수 없다"""
        with pytest.raises(ValueError, match="content는 비어있을 수 없습니다"):
            Message(role="user", content="   ")