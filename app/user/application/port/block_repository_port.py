from abc import ABC, abstractmethod
from app.user.domain.block import Block


class BlockRepositoryPort(ABC):
    """차단 저장소 포트 (인터페이스)"""

    @abstractmethod
    def save(self, block: Block) -> None:
        """차단을 저장한다"""
        pass

    @abstractmethod
    def find_by_id(self, block_id: str) -> Block | None:
        """id로 차단을 조회한다"""
        pass

    @abstractmethod
    def find_by_blocker_and_blocked(self, blocker_id: str, blocked_user_id: str) -> Block | None:
        """특정 차단 관계를 조회한다 (중복 차단 체크용)"""
        pass

    @abstractmethod
    def delete(self, block: Block) -> None:
        """차단을 삭제한다 (차단 해제)"""
        pass

    @abstractmethod
    def get_blocked_user_ids(self, blocker_id: str) -> list[str]:
        """차단한 유저 id 목록을 조회한다"""
        pass

    @abstractmethod
    def get_blocker_ids(self, blocked_user_id: str) -> list[str]:
        """나를 차단한 유저 id 목록을 조회한다"""
        pass
