from uuid import uuid4
from collections.abc import Callable

from app.chat.application.port.rating_repository_port import RatingRepositoryPort
from app.chat.application.dto.rate_user_request import RateUserRequest
from app.chat.domain.rating import Rating


class RateUserUseCase:
    """사용자 평가 유스케이스"""

    def __init__(
        self,
        rating_repo: RatingRepositoryPort,
        uuid_generator: Callable[[], any],
    ):
        self._rating_repo = rating_repo
        self._uuid_generator = uuid_generator

    def execute(self, request: RateUserRequest) -> None:
        """사용자 평가를 생성하고 저장한다"""
        # 이미 평가했는지 확인
        existing_rating = self._rating_repo.find_by_room_id_and_rater_id(
            room_id=request.room_id, rater_id=request.rater_id
        )
        if existing_rating:
            raise ValueError("이미 이 채팅방에서 사용자를 평가했습니다")

        # 새로운 평가 생성
        new_rating = Rating(
            id=str(self._uuid_generator()),
            rater_id=request.rater_id,
            rated_user_id=request.rated_user_id,
            room_id=request.room_id,
            score=request.score,
            feedback=request.feedback,
        )

        # 저장
        self._rating_repo.save(new_rating)
