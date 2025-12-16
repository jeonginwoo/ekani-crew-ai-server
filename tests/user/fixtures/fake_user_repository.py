from app.user.application.port.user_repository_port import UserRepositoryPort
from app.user.domain.user import User


class FakeUserRepository(UserRepositoryPort):
    """테스트용 Fake User 저장소"""

    def __init__(self):
        self._users_by_id: dict[str, User] = {}
        self._users_by_email: dict[str, User] = {}

    def save(self, user: User) -> None:
        self._users_by_id[user.id] = user
        self._users_by_email[user.email] = user

    def find_by_id(self, user_id: str) -> User | None:
        return self._users_by_id.get(user_id)

    def find_by_email(self, email: str) -> User | None:
        return self._users_by_email.get(email)
