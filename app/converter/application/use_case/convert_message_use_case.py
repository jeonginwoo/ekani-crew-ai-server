"""ConvertMessageUseCase - 3가지 톤 동시 생성"""

from typing import List

from app.converter.application.port.message_converter_port import MessageConverterPort
from app.converter.domain.tone_message import ToneMessage
from app.shared.vo.mbti import MBTI


class ConvertMessageUseCase:
    """메시지를 3가지 톤으로 동시에 변환하는 유스케이스"""

    TONES = ["공손한", "캐주얼한", "간결한"]

    def __init__(self, converter: MessageConverterPort):
        """초기화

        Args:
            converter: MessageConverterPort 구현체
        """
        self.converter = converter

    def execute(
        self,
        original_message: str,
        sender_mbti: MBTI,
        receiver_mbti: MBTI,
    ) -> List[ToneMessage]:
        """메시지를 3가지 톤으로 변환

        Args:
            original_message: 원본 메시지
            sender_mbti: 발신자 MBTI
            receiver_mbti: 수신자 MBTI

        Returns:
            List[ToneMessage]: 3가지 톤으로 변환된 메시지 목록
        """
        results = []

        for tone in self.TONES:
            tone_message = self.converter.convert(
                original_message=original_message,
                sender_mbti=sender_mbti,
                receiver_mbti=receiver_mbti,
                tone=tone,
            )
            results.append(tone_message)

        return results
