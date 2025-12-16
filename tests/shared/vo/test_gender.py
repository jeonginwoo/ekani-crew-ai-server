import pytest
from app.shared.vo.gender import Gender


def test_gender_creates_from_valid_string():
    """유효한 성별 문자열로 객체를 생성할 수 있다"""
    # Given: 유효한 성별 문자열
    male = "MALE"
    female = "FEMALE"

    # When: Gender 객체를 생성하면
    gender_male = Gender(male)
    gender_female = Gender(female)

    # Then: 정상적으로 생성되고 값을 조회할 수 있다
    assert gender_male.value == "MALE"
    assert gender_female.value == "FEMALE"


def test_gender_rejects_invalid_value():
    """유효하지 않은 성별 값을 거부한다"""
    # Given: 유효하지 않은 성별 문자열들
    invalid_genders = ["UNKNOWN", "OTHER", "M", "F", "", "male", "female"]

    # When & Then: Gender 객체 생성 시 ValueError가 발생한다
    for invalid_gender in invalid_genders:
        with pytest.raises(ValueError):
            Gender(invalid_gender)
