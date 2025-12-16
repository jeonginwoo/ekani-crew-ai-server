"""메시지 변환 요청 DTO"""

from pydantic import BaseModel, Field, field_validator


class ConvertRequest(BaseModel):
    """메시지 변환 요청

    Attributes:
        original_message: 원본 메시지
        sender_mbti: 발신자 MBTI
        receiver_mbti: 수신자 MBTI
        tone: 변환할 톤
    """

    original_message: str = Field(..., min_length=1, description="원본 메시지")
    sender_mbti: str = Field(..., description="발신자 MBTI (예: INTJ)")
    receiver_mbti: str = Field(..., description="수신자 MBTI (예: ESTP)")
    tone: str = Field(..., min_length=1, description="변환할 톤 (예: 공손한, 캐주얼한, 간결한)")

    @field_validator("sender_mbti", "receiver_mbti")
    @classmethod
    def validate_mbti(cls, v: str) -> str:
        """MBTI 유효성 검증"""
        valid_types = [
            "INTJ", "INTP", "ENTJ", "ENTP",
            "INFJ", "INFP", "ENFJ", "ENFP",
            "ISTJ", "ISFJ", "ESTJ", "ESFJ",
            "ISTP", "ISFP", "ESTP", "ESFP"
        ]
        if v.upper() not in valid_types:
            raise ValueError(f"유효하지 않은 MBTI 타입입니다: {v}")
        return v.upper()
