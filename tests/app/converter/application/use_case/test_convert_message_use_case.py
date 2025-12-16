"""ConvertMessageUseCase 테스트"""

import pytest
from unittest.mock import Mock

from app.converter.domain.tone_message import ToneMessage
from app.shared.vo.mbti import MBTI


class TestConvertMessageUseCase:
    """ConvertMessageUseCase 테스트"""

    def test_should_generate_three_tones_simultaneously(self):
        """3가지 톤을 동시에 생성해야 함"""
        # Given
        from app.converter.application.use_case.convert_message_use_case import (
            ConvertMessageUseCase,
        )

        mock_converter = Mock()
        mock_converter.convert.side_effect = [
            ToneMessage(
                tone="공손한",
                content="안녕하세요, 내일 회의 시간을 조정해주실 수 있을까요?",
                explanation="공손한 표현이 효과적입니다.",
            ),
            ToneMessage(
                tone="캐주얼한",
                content="내일 회의 시간 바꿀 수 있어?",
                explanation="캐주얼한 표현이 효과적입니다.",
            ),
            ToneMessage(
                tone="간결한",
                content="회의 시간 변경 가능?",
                explanation="간결한 표현이 효과적입니다.",
            ),
        ]

        use_case = ConvertMessageUseCase(converter=mock_converter)

        # When
        results = use_case.execute(
            original_message="내일 회의 시간 바꿀 수 있어?",
            sender_mbti=MBTI("INTJ"),
            receiver_mbti=MBTI("ESTP"),
        )

        # Then
        assert len(results) == 3
        assert results[0].tone == "공손한"
        assert results[1].tone == "캐주얼한"
        assert results[2].tone == "간결한"

        # Converter가 3번 호출되었는지 확인
        assert mock_converter.convert.call_count == 3

    def test_should_call_converter_with_each_tone(self):
        """각 톤에 대해 converter를 호출해야 함"""
        # Given
        from app.converter.application.use_case.convert_message_use_case import (
            ConvertMessageUseCase,
        )

        mock_converter = Mock()
        mock_converter.convert.return_value = ToneMessage(
            tone="공손한", content="변환된 메시지", explanation="설명"
        )

        use_case = ConvertMessageUseCase(converter=mock_converter)

        # When
        use_case.execute(
            original_message="테스트",
            sender_mbti=MBTI("INTJ"),
            receiver_mbti=MBTI("ESTP"),
        )

        # Then
        calls = mock_converter.convert.call_args_list
        assert len(calls) == 3

        # 각 호출에서 톤이 다른지 확인
        tones = [call.kwargs["tone"] for call in calls]
        assert "공손한" in tones
        assert "캐주얼한" in tones
        assert "간결한" in tones

    def test_should_pass_mbti_to_converter(self):
        """MBTI 정보를 converter에 전달해야 함"""
        # Given
        from app.converter.application.use_case.convert_message_use_case import (
            ConvertMessageUseCase,
        )

        mock_converter = Mock()
        mock_converter.convert.return_value = ToneMessage(
            tone="공손한", content="변환된 메시지", explanation="설명"
        )

        use_case = ConvertMessageUseCase(converter=mock_converter)

        sender_mbti = MBTI("INTJ")
        receiver_mbti = MBTI("ESTP")

        # When
        use_case.execute(
            original_message="테스트",
            sender_mbti=sender_mbti,
            receiver_mbti=receiver_mbti,
        )

        # Then
        first_call = mock_converter.convert.call_args_list[0]
        assert first_call.kwargs["sender_mbti"] == sender_mbti
        assert first_call.kwargs["receiver_mbti"] == receiver_mbti
        assert first_call.kwargs["original_message"] == "테스트"
