"""MessageConverterPort 인터페이스"""

from abc import ABC, abstractmethod

from app.converter.domain.tone_message import ToneMessage
from app.shared.vo.mbti import MBTI


class MessageConverterPort(ABC):
    """메시지 변환 포트 인터페이스

    메시지를 특정 톤으로 변환하는 기능을 정의합니다.
    """

    @abstractmethod
    def convert(
        self,
        original_message: str,
        sender_mbti: MBTI,
        receiver_mbti: MBTI,
        tone: str
    ) -> ToneMessage:
        """메시지를 특정 톤으로 변환

        Args:
            original_message: 원본 메시지
            sender_mbti: 발신자 MBTI
            receiver_mbti: 수신자 MBTI
            tone: 변환할 톤 (예: "공손한", "캐주얼한", "간결한")

        Returns:
            ToneMessage: 변환된 메시지
        """
        pass
