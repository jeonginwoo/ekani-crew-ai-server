from datetime import datetime


class Message:
    """상담 메시지 도메인"""

    VALID_ROLES = ("user", "assistant")

    def __init__(
        self,
        role: str,
        content: str,
        timestamp: datetime | None = None,
    ):
        self._validate(role, content)
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now()

    def _validate(self, role: str, content: str) -> None:
        if role not in self.VALID_ROLES:
            raise ValueError(f"role은 'user' 또는 'assistant'만 허용됩니다: {role}")
        if not content or not content.strip():
            raise ValueError("content는 비어있을 수 없습니다")