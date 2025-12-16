import pytest
from app.shared.vo.mbti import MBTI


def test_mbti_creates_from_valid_string():
    """유효한 MBTI 문자열로 객체를 생성할 수 있다"""
    # Given: 유효한 MBTI 문자열
    mbti_string = "INTJ"

    # When: MBTI 객체를 생성하면
    mbti = MBTI(mbti_string)

    # Then: 정상적으로 생성되고 값을 조회할 수 있다
    assert mbti.value == "INTJ"


def test_mbti_rejects_invalid_format():
    """유효하지 않은 MBTI 형식을 거부한다"""
    # Given: 유효하지 않은 MBTI 문자열들
    invalid_mbtis = ["XXXX", "INXX", "ABCD", "IN", "INTJJ", ""]

    # When & Then: MBTI 객체 생성 시 ValueError가 발생한다
    for invalid_mbti in invalid_mbtis:
        with pytest.raises(ValueError):
            MBTI(invalid_mbti)


def test_mbti_provides_individual_dimension_access():
    """MBTI 각 차원을 개별적으로 접근할 수 있다"""
    # Given: MBTI 객체
    mbti = MBTI("INTJ")

    # When & Then: 각 차원을 개별적으로 조회할 수 있다
    assert mbti.energy == "I"  # E/I (외향/내향)
    assert mbti.information == "N"  # S/N (감각/직관)
    assert mbti.decision == "T"  # T/F (사고/감정)
    assert mbti.lifestyle == "J"  # J/P (판단/인식)
