import pytest
from app.auth.domain.oauth_identity import OAuthIdentity


def test_create_oauth_identity_with_valid_values():
    """유효한 provider, provider_user_id, email로 OAuthIdentity 객체를 생성할 수 있다"""
    # Given: 유효한 값들
    provider = "google"
    provider_user_id = "google-abc-xyz"
    email = "test@example.com"

    # When: OAuthIdentity 객체를 생성하면
    identity = OAuthIdentity(
        provider=provider,
        provider_user_id=provider_user_id,
        email=email
    )

    # Then: 정상적으로 생성되고 값을 조회할 수 있다
    assert identity.provider == "google"
    assert identity.provider_user_id == "google-abc-xyz"
    assert identity.email == "test@example.com"


def test_reject_empty_provider():
    """빈 provider를 거부한다"""
    # Given: 빈 provider
    with pytest.raises(ValueError):
        OAuthIdentity(provider="", provider_user_id="abc", email="test@example.com")


def test_reject_empty_provider_user_id():
    """빈 provider_user_id를 거부한다"""
    # Given: 빈 provider_user_id
    with pytest.raises(ValueError):
        OAuthIdentity(provider="google", provider_user_id="", email="test@example.com")


def test_reject_empty_email():
    """빈 email을 거부한다"""
    # Given: 빈 email
    with pytest.raises(ValueError):
        OAuthIdentity(provider="google", provider_user_id="abc", email="")


def test_accept_google_provider():
    """유효한 provider 'google'을 허용한다"""
    # Given: google provider
    identity = OAuthIdentity(
        provider="google",
        provider_user_id="google-abc-xyz",
        email="test@gmail.com"
    )

    # Then: 정상적으로 생성된다
    assert identity.provider == "google"


def test_accept_kakao_provider():
    """유효한 provider 'kakao'를 허용한다"""
    # Given: kakao provider
    identity = OAuthIdentity(
        provider="kakao",
        provider_user_id="kakao-def-uvw",
        email="test@kakao.com"
    )

    # Then: 정상적으로 생성된다
    assert identity.provider == "kakao"


def test_reject_invalid_provider():
    """유효하지 않은 provider를 거부한다"""
    # Given: 유효하지 않은 provider들
    invalid_providers = ["facebook", "twitter", "naver", "GOOGLE", "KAKAO"]

    # When & Then: OAuthIdentity 객체 생성 시 ValueError가 발생한다
    for invalid_provider in invalid_providers:
        with pytest.raises(ValueError):
            OAuthIdentity(
                provider=invalid_provider,
                provider_user_id="some-user-id",
                email="test@example.com"
            )
