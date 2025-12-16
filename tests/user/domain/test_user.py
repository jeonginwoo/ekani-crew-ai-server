import pytest
from app.user.domain.user import User
from app.shared.vo.mbti import MBTI
from app.shared.vo.gender import Gender


def test_user_creates_with_id_and_email():
    """유효한 id와 email로 User 객체를 생성할 수 있다"""
    # Given: 유효한 user_id와 email
    user_id = "user-123"
    email = "test@example.com"

    # When: User 객체를 생성하면
    user = User(id=user_id, email=email)

    # Then: 정상적으로 생성되고 값을 조회할 수 있다
    assert user.id == "user-123"
    assert user.email == "test@example.com"


def test_user_rejects_empty_id():
    """빈 id를 거부한다"""
    # Given: 빈 user_id
    user_id = ""
    email = "test@example.com"

    # When & Then: User 객체 생성 시 ValueError가 발생한다
    with pytest.raises(ValueError):
        User(id=user_id, email=email)


def test_user_rejects_empty_email():
    """빈 email을 거부한다"""
    # Given: 빈 email
    user_id = "user-123"
    email = ""

    # When & Then: User 객체 생성 시 ValueError가 발생한다
    with pytest.raises(ValueError):
        User(id=user_id, email=email)


def test_user_creates_with_optional_mbti_and_gender():
    """mbti와 gender 없이 User 객체를 생성할 수 있다"""
    # Given: mbti와 gender 없이
    user = User(id="user-123", email="test@example.com")

    # Then: mbti와 gender는 None이다
    assert user.mbti is None
    assert user.gender is None


def test_user_creates_with_mbti_and_gender():
    """mbti와 gender를 포함하여 User 객체를 생성할 수 있다"""
    # Given: mbti와 gender
    mbti = MBTI("INTJ")
    gender = Gender("MALE")

    # When: User 객체를 생성하면
    user = User(id="user-123", email="test@example.com", mbti=mbti, gender=gender)

    # Then: mbti와 gender 값을 조회할 수 있다
    assert user.mbti.value == "INTJ"
    assert user.gender.value == "MALE"