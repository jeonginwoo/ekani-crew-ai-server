"""ToneMessage 도메인 객체 테스트"""

import pytest


class TestToneMessage:
    """ToneMessage 도메인 객체 테스트"""

    def test_should_create_tone_message_with_valid_data(self):
        """유효한 데이터로 ToneMessage 객체를 생성할 수 있어야 함"""
        # Given
        from app.converter.domain.tone_message import ToneMessage

        tone = "공손한"
        content = "안녕하세요, 내일 회의 시간을 조정해주실 수 있을까요?"
        explanation = "ESTP 유형에게는 직설적이면서도 존중하는 표현이 효과적입니다."

        # When
        message = ToneMessage(
            tone=tone,
            content=content,
            explanation=explanation
        )

        # Then
        assert message.tone == tone
        assert message.content == content
        assert message.explanation == explanation

    def test_should_reject_empty_tone(self):
        """빈 톤은 거부되어야 함"""
        # Given
        from app.converter.domain.tone_message import ToneMessage

        # When & Then
        with pytest.raises(ValueError, match="톤은 비어있을 수 없습니다"):
            ToneMessage(
                tone="",
                content="내용",
                explanation="설명"
            )

    def test_should_reject_empty_content(self):
        """빈 내용은 거부되어야 함"""
        # Given
        from app.converter.domain.tone_message import ToneMessage

        # When & Then
        with pytest.raises(ValueError, match="내용은 비어있을 수 없습니다"):
            ToneMessage(
                tone="공손한",
                content="",
                explanation="설명"
            )

    def test_should_reject_empty_explanation(self):
        """빈 설명은 거부되어야 함"""
        # Given
        from app.converter.domain.tone_message import ToneMessage

        # When & Then
        with pytest.raises(ValueError, match="설명은 비어있을 수 없습니다"):
            ToneMessage(
                tone="공손한",
                content="내용",
                explanation=""
            )
