"""3가지 톤 변환 응답 DTO"""

from typing import List
from pydantic import BaseModel, Field

from app.converter.domain.tone_message import ToneMessage


class ToneMessageResponse(BaseModel):
    """개별 톤 메시지 응답

    Attributes:
        tone: 메시지의 톤
        content: 변환된 메시지 내용
        explanation: 왜 이 표현이 효과적인지에 대한 설명
    """

    tone: str = Field(..., description="메시지의 톤")
    content: str = Field(..., description="변환된 메시지 내용")
    explanation: str = Field(..., description="효과적인 이유 설명")


class ConvertThreeTonesResponse(BaseModel):
    """3가지 톤 변환 응답

    Attributes:
        tones: 3가지 톤으로 변환된 메시지 목록
    """

    tones: List[ToneMessageResponse] = Field(
        ..., description="3가지 톤으로 변환된 메시지 목록"
    )

    @classmethod
    def from_domain(cls, tone_messages: List[ToneMessage]) -> "ConvertThreeTonesResponse":
        """도메인 객체 리스트로부터 응답 DTO 생성

        Args:
            tone_messages: ToneMessage 도메인 객체 리스트

        Returns:
            ConvertThreeTonesResponse: 응답 DTO
        """
        tone_responses = [
            ToneMessageResponse(
                tone=tm.tone, content=tm.content, explanation=tm.explanation
            )
            for tm in tone_messages
        ]
        return cls(tones=tone_responses)
