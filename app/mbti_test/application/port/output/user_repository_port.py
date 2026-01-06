from abc import ABC, abstractmethod
import uuid
from typing import Any


class UserRepositoryPort(ABC):
    """
    User 리포지토리 포트.
    """

    @abstractmethod
    def find_by_id(self, user_id: uuid.UUID) -> Any | None:
        pass

    @abstractmethod
    def update_mbti(self, user_id: uuid.UUID, mbti: str) -> None:
        """MBTI-4 결과 분석 후 사용자의 MBTI를 업데이트한다."""
        raise NotImplementedError

