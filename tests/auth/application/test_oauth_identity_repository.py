import pytest

from app.auth.domain.oauth_identity import OAuthIdentity
from tests.auth.fixtures.fake_oauth_identity_repository import (
    FakeOAuthIdentityRepository,
)


@pytest.fixture
def repository():
    """테스트용 Fake OAuthIdentity 저장소"""
    return FakeOAuthIdentityRepository()


def test_save_and_find_oauth_identity(repository):
    """OAuthIdentity를 저장하고 provider/provider_user_id로 조회할 수 있다"""
    identity = OAuthIdentity(
        provider="google",
        provider_user_id="google-123",
        email="test@gmail.com",
    )

    repository.save(identity)
    found = repository.find_by_provider_and_provider_user_id("google", "google-123")

    assert found is not None
    assert found.provider == "google"
    assert found.provider_user_id == "google-123"
    assert found.email == "test@gmail.com"


def test_find_nonexistent_oauth_identity_returns_none(repository):
    """존재하지 않는 provider/provider_user_id로 조회하면 None을 반환한다"""
    found = repository.find_by_provider_and_provider_user_id("google", "nonexistent")
    assert found is None


def test_find_different_provider_returns_none(repository):
    """같은 provider_user_id라도 다른 provider면 None을 반환한다"""
    identity = OAuthIdentity(
        provider="google",
        provider_user_id="user-123",
        email="test@gmail.com",
    )
    repository.save(identity)

    found = repository.find_by_provider_and_provider_user_id("kakao", "user-123")
    assert found is None
