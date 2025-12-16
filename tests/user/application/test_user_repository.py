import pytest

from app.user.domain.user import User
from tests.user.fixtures.fake_user_repository import FakeUserRepository


@pytest.fixture
def repository():
    """테스트용 Fake User 저장소"""
    return FakeUserRepository()


def test_save_and_find_user_by_id(repository):
    """유저를 저장하고 id로 조회할 수 있다"""
    user = User(id="user-123", email="test@example.com")

    repository.save(user)
    found = repository.find_by_id("user-123")

    assert found is not None
    assert found.id == "user-123"
    assert found.email == "test@example.com"


def test_find_nonexistent_user_returns_none(repository):
    """존재하지 않는 id로 조회하면 None을 반환한다"""
    found = repository.find_by_id("nonexistent")
    assert found is None


def test_find_user_by_email(repository):
    """email로 유저를 조회할 수 있다"""
    user = User(id="user-123", email="test@example.com")
    repository.save(user)

    found = repository.find_by_email("test@example.com")

    assert found is not None
    assert found.id == "user-123"


def test_find_nonexistent_email_returns_none(repository):
    """존재하지 않는 email로 조회하면 None을 반환한다"""
    found = repository.find_by_email("nonexistent@example.com")
    assert found is None
