"""MessageConverterPort 인터페이스 테스트"""

import pytest
from abc import ABC

from app.converter.domain.tone_message import ToneMessage


class TestMessageConverterPort:
    """MessageConverterPort 인터페이스 테스트"""

    def test_should_be_abstract_interface(self):
        """MessageConverterPort는 추상 인터페이스여야 함"""
        # Given
        from app.converter.application.port.message_converter_port import MessageConverterPort

        # Then
        assert issubclass(MessageConverterPort, ABC)

    def test_should_have_convert_method(self):
        """convert 메서드를 가져야 함"""
        # Given
        from app.converter.application.port.message_converter_port import MessageConverterPort

        # Then
        assert hasattr(MessageConverterPort, "convert")

    def test_convert_method_should_accept_required_parameters(self):
        """convert 메서드는 필수 파라미터를 받아야 함"""
        # Given
        from app.converter.application.port.message_converter_port import MessageConverterPort
        from app.shared.vo.mbti import MBTI

        # Fake 구현체를 만들어 테스트
        class FakeMessageConverter(MessageConverterPort):
            def convert(
                self,
                original_message: str,
                sender_mbti: MBTI,
                receiver_mbti: MBTI,
                tone: str
            ) -> ToneMessage:
                return ToneMessage(
                    tone=tone,
                    content="변환된 메시지",
                    explanation="설명"
                )

        # When
        converter = FakeMessageConverter()
        result = converter.convert(
            original_message="안녕하세요",
            sender_mbti=MBTI("INTJ"),
            receiver_mbti=MBTI("ESTP"),
            tone="공손한"
        )

        # Then
        assert isinstance(result, ToneMessage)
        assert result.tone == "공손한"
