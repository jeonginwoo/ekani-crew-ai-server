from dataclasses import dataclass

@dataclass(frozen=True)
class RateUserRequest:
    rater_id: str
    rated_user_id: str
    room_id: str
    score: int
    feedback: str | None
