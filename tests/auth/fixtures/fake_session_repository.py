from app.auth.application.port.session_repository_port import SessionRepositoryPort
from app.auth.domain.session import Session


class FakeSessionRepository(SessionRepositoryPort):
    """테스트용 Fake Session 저장소"""

    def __init__(self):
        self._sessions: dict[str, Session] = {}

    def save(self, session: Session) -> None:
        self._sessions[session.session_id] = session

    def find_by_session_id(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)

    def delete(self, session_id: str) -> None:
        if session_id in self._sessions:
            del self._sessions[session_id]
