from sqlalchemy.orm import Session

from app.user.application.port.user_repository_port import UserRepositoryPort
from app.user.domain.user import User
from app.user.infrastructure.model.user_model import UserModel
from app.shared.vo.mbti import MBTI
from app.shared.vo.gender import Gender


class MySQLUserRepository(UserRepositoryPort):
    """MySQL 기반 유저 저장소"""

    def __init__(self, db_session: Session):
        self._db = db_session

    def save(self, user: User) -> None:
        """유저를 저장한다 (upsert)"""
        existing = self._db.query(UserModel).filter(
            UserModel.id == user.id
        ).first()

        if existing:
            existing.email = user.email
            existing.mbti = user.mbti.value if user.mbti else None
            existing.gender = user.gender.value if user.gender else None
        else:
            model = UserModel(
                id=user.id,
                email=user.email,
                mbti=user.mbti.value if user.mbti else None,
                gender=user.gender.value if user.gender else None,
            )
            self._db.add(model)

        self._db.commit()

    def find_by_id(self, user_id: str) -> User | None:
        """id로 유저를 조회한다"""
        model = self._db.query(UserModel).filter(
            UserModel.id == user_id
        ).first()

        if model is None:
            return None

        return self._to_domain(model)

    def find_by_email(self, email: str) -> User | None:
        """email로 유저를 조회한다"""
        model = self._db.query(UserModel).filter(
            UserModel.email == email
        ).first()

        if model is None:
            return None

        return self._to_domain(model)

    def _to_domain(self, model: UserModel) -> User:
        """ORM 모델을 도메인 객체로 변환"""
        return User(
            id=model.id,
            email=model.email,
            mbti=MBTI(model.mbti) if model.mbti else None,
            gender=Gender(model.gender) if model.gender else None,
        )
