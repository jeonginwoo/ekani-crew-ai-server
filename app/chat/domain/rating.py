from datetime import datetime

class Rating:
    """채팅방 사용자 평가 도메인 엔티티"""

    def __init__(
        self,
        id: str,
        rater_id: str,
        rated_user_id: str,
        room_id: str,
        score: int,
        feedback: str | None,
        created_at: datetime | None = None,
    ):
        self._validate(rater_id, rated_user_id, room_id, score)
        self.id = id
        self.rater_id = rater_id
        self.rated_user_id = rated_user_id
        self.room_id = room_id
        self.score = score
        self.feedback = feedback
        self.created_at = created_at or datetime.now()

    def _validate(self, rater_id: str, rated_user_id: str, room_id: str, score: int) -> None:
        """Rating 값의 유효성을 검증한다"""
        if not rater_id:
            raise ValueError("rater_id는 비어있을 수 없습니다")
        if not rated_user_id:
            raise ValueError("rated_user_id는 비어있을 수 없습니다")
        if not room_id:
            raise ValueError("room_id는 비어있을 수 없습니다")
        if not 1 <= score <= 5:
            raise ValueError("점수는 1에서 5 사이여야 합니다")
