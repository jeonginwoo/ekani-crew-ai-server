"""ToneMessage 도메인 객체"""

from dataclasses import dataclass


@dataclass
class ToneMessage:
    """특정 톤으로 변환된 메시지

    Attributes:
        tone: 메시지의 톤 (예: "공손한", "캐주얼한", "간결한")
        content: 변환된 메시지 내용
        explanation: 왜 이 표현이 효과적인지에 대한 설명
    """
    tone: str
    content: str
    explanation: str

    def __post_init__(self):
        """유효성 검증"""
        if not self.tone or not self.tone.strip():
            raise ValueError("톤은 비어있을 수 없습니다")
        if not self.content or not self.content.strip():
            raise ValueError("내용은 비어있을 수 없습니다")
        if not self.explanation or not self.explanation.strip():
            raise ValueError("설명은 비어있을 수 없습니다")
