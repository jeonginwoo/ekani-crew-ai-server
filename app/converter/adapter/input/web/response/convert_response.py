"""메시지 변환 응답 DTO"""

from pydantic import BaseModel, Field

from app.converter.domain.tone_message import ToneMessage


class ConvertResponse(BaseModel):
    """메시지 변환 응답

    Attributes:
        tone: 메시지의 톤
        content: 변환된 메시지 내용
        explanation: 왜 이 표현이 효과적인지에 대한 설명
    """

    tone: str = Field(..., description="메시지의 톤")
    content: str = Field(..., description="변환된 메시지 내용")
    explanation: str = Field(..., description="효과적인 이유 설명")

    @classmethod
    def from_domain(cls, tone_message: ToneMessage) -> "ConvertResponse":
        """도메인 객체로부터 응답 DTO 생성

        Args:
            tone_message: ToneMessage 도메인 객체

        Returns:
            ConvertResponse: 응답 DTO
        """
        return cls(
            tone=tone_message.tone,
            content=tone_message.content,
            explanation=tone_message.explanation,
        )
