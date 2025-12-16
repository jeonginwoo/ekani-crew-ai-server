from abc import ABC, abstractmethod

from app.consult.domain.consult_session import ConsultSession


class ConsultRepositoryPort(ABC):
    """상담 세션 저장소 포트 인터페이스"""

    @abstractmethod
    def save(self, session: ConsultSession) -> None:
        """세션을 저장한다"""
        pass

    @abstractmethod
    def find_by_id(self, session_id: str) -> ConsultSession | None:
        """id로 세션을 조회한다"""
        pass

    @abstractmethod
    def find_completed_by_user_id(self, user_id: str) -> list[ConsultSession]:
        """user_id로 완료된 세션 목록을 조회한다"""
        pass
