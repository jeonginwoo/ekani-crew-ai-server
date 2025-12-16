class Gender:
    """Gender 값 객체"""

    _VALID_VALUES = ["MALE", "FEMALE"]

    def __init__(self, value: str):
        self._validate(value)
        self.value = value

    def _validate(self, value: str) -> None:
        """Gender 값의 유효성을 검증한다"""
        if value not in self._VALID_VALUES:
            valid_values = "/".join(self._VALID_VALUES)
            raise ValueError(f"Gender는 {valid_values} 중 하나여야 합니다: {value}")
