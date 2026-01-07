from app.mbti_test.application.port.output.mbti_test_session_repository import MBTITestSessionRepositoryPort


class DeleteInProgressTestUseCase:
    def __init__(self, session_repository: MBTITestSessionRepositoryPort):
        self._session_repository = session_repository

    def execute(self, user_id: str) -> None:
        session = self._session_repository.find_by_user_id_and_status(user_id, "IN_PROGRESS")
        if session:
            self._session_repository.delete(session)