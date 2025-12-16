import pytest
from app.consult.domain.analysis import Analysis


def test_analysis_creates_with_all_sections():
    """4개 섹션으로 Analysis를 생성할 수 있다"""
    # Given: 분석 섹션들
    situation = "두 사람의 갈등 상황 분석..."
    traits = "INTJ의 특성상 논리적 접근..."
    solutions = "1. 감정을 먼저 인정하기..."
    cautions = "상대방의 F 성향을 고려..."

    # When: Analysis 생성
    analysis = Analysis(
        situation=situation,
        traits=traits,
        solutions=solutions,
        cautions=cautions
    )

    # Then: 모든 섹션이 저장됨
    assert analysis.situation == situation
    assert analysis.traits == traits
    assert analysis.solutions == solutions
    assert analysis.cautions == cautions


def test_analysis_rejects_empty_situation():
    """빈 situation을 거부한다"""
    with pytest.raises(ValueError, match="situation"):
        Analysis(
            situation="",
            traits="traits",
            solutions="solutions",
            cautions="cautions"
        )


def test_analysis_rejects_empty_traits():
    """빈 traits를 거부한다"""
    with pytest.raises(ValueError, match="traits"):
        Analysis(
            situation="situation",
            traits="",
            solutions="solutions",
            cautions="cautions"
        )


def test_analysis_rejects_empty_solutions():
    """빈 solutions를 거부한다"""
    with pytest.raises(ValueError, match="solutions"):
        Analysis(
            situation="situation",
            traits="traits",
            solutions="",
            cautions="cautions"
        )


def test_analysis_rejects_empty_cautions():
    """빈 cautions를 거부한다"""
    with pytest.raises(ValueError, match="cautions"):
        Analysis(
            situation="situation",
            traits="traits",
            solutions="solutions",
            cautions=""
        )


def test_analysis_to_dict():
    """Analysis를 dict로 변환할 수 있다"""
    # Given: Analysis 객체
    analysis = Analysis(
        situation="상황 분석",
        traits="특성 분석",
        solutions="해결책",
        cautions="주의사항"
    )

    # When: dict로 변환
    result = analysis.to_dict()

    # Then: 모든 필드가 포함됨
    assert result == {
        "situation": "상황 분석",
        "traits": "특성 분석",
        "solutions": "해결책",
        "cautions": "주의사항"
    }
