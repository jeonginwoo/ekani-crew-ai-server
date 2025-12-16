import pytest

from app.consult.domain.consult_session import ConsultSession
from app.shared.vo.mbti import MBTI
from app.shared.vo.gender import Gender
from tests.consult.fixtures.fake_consult_repository import FakeConsultRepository


@pytest.fixture
def repository():
    """테스트용 Fake Consult 저장소"""
    return FakeConsultRepository()


def test_save_and_find_session_by_id(repository):
    """세션을 저장하고 id로 조회할 수 있다"""
    # Given: 유효한 상담 세션
    session = ConsultSession(
        id="session-123",
        user_id="user-456",
        mbti=MBTI("INTJ"),
        gender=Gender("MALE")
    )

    # When: 세션을 저장하고 조회하면
    repository.save(session)
    found = repository.find_by_id("session-123")

    # Then: 저장된 세션을 찾을 수 있다
    assert found is not None
    assert found.id == "session-123"
    assert found.user_id == "user-456"
    assert found.mbti.value == "INTJ"
    assert found.gender.value == "MALE"


def test_find_nonexistent_session_returns_none(repository):
    """존재하지 않는 id로 조회하면 None을 반환한다"""
    # When: 존재하지 않는 세션을 조회하면
    found = repository.find_by_id("nonexistent")

    # Then: None을 반환한다
    assert found is None
