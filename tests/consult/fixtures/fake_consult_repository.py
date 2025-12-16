from app.consult.application.port.consult_repository_port import ConsultRepositoryPort
from app.consult.domain.consult_session import ConsultSession


class FakeConsultRepository(ConsultRepositoryPort):
    """테스트용 Fake Consult 저장소"""

    def __init__(self):
        self._sessions: dict[str, ConsultSession] = {}

    def save(self, session: ConsultSession) -> None:
        self._sessions[session.id] = session

    def find_by_id(self, session_id: str) -> ConsultSession | None:
        return self._sessions.get(session_id)

    def find_completed_by_user_id(self, user_id: str) -> list[ConsultSession]:
        return [
            session for session in self._sessions.values()
            if session.user_id == user_id and session.is_completed()
        ]
