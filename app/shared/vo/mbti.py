class MBTI:
    """MBTI 값 객체"""

    _VALID_DIMENSIONS = [
        ["E", "I"],  # 외향/내향
        ["S", "N"],  # 감각/직관
        ["T", "F"],  # 사고/감정
        ["J", "P"],  # 판단/인식
    ]

    def __init__(self, value: str):
        upper_value = value.upper()
        self._validate(upper_value)
        self.value = upper_value
        self.energy = upper_value[0]
        self.information = upper_value[1]
        self.decision = upper_value[2]
        self.lifestyle = upper_value[3]

    def _validate(self, value: str) -> None:
        """MBTI 값의 유효성을 검증한다"""
        if len(value) != 4:
            raise ValueError(f"MBTI는 4글자여야 합니다: {value}")

        for i, char in enumerate(value):
            if char not in self._VALID_DIMENSIONS[i]:
                valid_chars = "/".join(self._VALID_DIMENSIONS[i])
                raise ValueError(
                    f"MBTI {i+1}번째 글자는 {valid_chars} 중 하나여야 합니다: {char}"
                )