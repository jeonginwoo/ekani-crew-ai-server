from sqlalchemy.orm import Session
from app.chat.application.port.rating_repository_port import RatingRepositoryPort
from app.chat.domain.rating import Rating
from app.chat.infrastructure.model.rating_model import RatingModel

class MySQLRatingRepository(RatingRepositoryPort):
    """MySQL 기반 평가 저장소"""

    def __init__(self, db_session: Session):
        self._db = db_session

    def save(self, rating: Rating) -> None:
        """평가를 저장한다"""
        rating_model = RatingModel(
            id=rating.id,
            rater_id=rating.rater_id,
            rated_user_id=rating.rated_user_id,
            room_id=rating.room_id,
            score=rating.score,
            feedback=rating.feedback,
            created_at=rating.created_at,
        )
        self._db.add(rating_model)
        self._db.commit()

    def find_by_room_id_and_rater_id(self, room_id: str, rater_id: str) -> Rating | None:
        """채팅방 ID와 평가자 ID로 평가를 조회한다"""
        rating_model = (
            self._db.query(RatingModel)
            .filter_by(room_id=room_id, rater_id=rater_id)
            .first()
        )

        if not rating_model:
            return None

        return Rating(
            id=rating_model.id,
            rater_id=rating_model.rater_id,
            rated_user_id=rating_model.rated_user_id,
            room_id=rating_model.room_id,
            score=rating_model.score,
            feedback=rating_model.feedback,
            created_at=rating_model.created_at,
        )
