import json
from sqlalchemy.orm import Session

from app.consult.application.port.consult_repository_port import ConsultRepositoryPort
from app.consult.domain.consult_session import ConsultSession
from app.consult.domain.message import Message
from app.consult.infrastructure.model.consult_session_model import ConsultSessionModel
from app.consult.infrastructure.model.consult_message_model import ConsultMessageModel
from app.shared.vo.mbti import MBTI
from app.shared.vo.gender import Gender


class MySQLConsultRepository(ConsultRepositoryPort):
    """MySQL 기반 상담 세션 저장소"""

    def __init__(self, db_session: Session):
        self._db = db_session

    def save(self, session: ConsultSession) -> None:
        """세션을 저장한다 (insert 또는 update)"""
        # 분석 결과를 JSON으로 변환
        analysis_json = None
        if session.get_analysis():
            analysis_json = json.dumps(session.get_analysis(), ensure_ascii=False)

        # 세션 저장 (merge로 insert/update 처리)
        session_model = ConsultSessionModel(
            id=session.id,
            user_id=session.user_id,
            mbti=session.mbti.value,
            gender=session.gender.value,
            created_at=session.created_at,
            is_completed=session.is_completed(),
            analysis_json=analysis_json,
        )
        self._db.merge(session_model)

        # 기존 메시지 삭제 후 새로 저장 (단순한 구현)
        self._db.query(ConsultMessageModel).filter(
            ConsultMessageModel.session_id == session.id
        ).delete()

        # 메시지 저장
        for msg in session.get_messages():
            message_model = ConsultMessageModel(
                session_id=session.id,
                role=msg.role,
                content=msg.content,
                created_at=msg.timestamp,
            )
            self._db.add(message_model)

        self._db.commit()

    def find_by_id(self, session_id: str) -> ConsultSession | None:
        """id로 세션을 조회한다"""
        session_model = self._db.query(ConsultSessionModel).filter(
            ConsultSessionModel.id == session_id
        ).first()

        if session_model is None:
            return None

        # 메시지 조회 (생성 시간순)
        message_models = self._db.query(ConsultMessageModel).filter(
            ConsultMessageModel.session_id == session_id
        ).order_by(ConsultMessageModel.id).all()

        messages = [
            Message(
                role=m.role,
                content=m.content,
                timestamp=m.created_at,
            )
            for m in message_models
        ]

        # 분석 결과 파싱
        analysis = None
        if session_model.analysis_json:
            analysis = json.loads(session_model.analysis_json)

        return ConsultSession(
            id=session_model.id,
            user_id=session_model.user_id,
            mbti=MBTI(session_model.mbti),
            gender=Gender(session_model.gender),
            created_at=session_model.created_at,
            messages=messages,
            completed=session_model.is_completed or False,
            analysis=analysis,
        )

    def find_completed_by_user_id(self, user_id: str) -> list[ConsultSession]:
        """user_id로 완료된 세션 목록을 조회한다 (최신순)"""
        session_models = self._db.query(ConsultSessionModel).filter(
            ConsultSessionModel.user_id == user_id,
            ConsultSessionModel.is_completed == True
        ).order_by(ConsultSessionModel.created_at.desc()).all()

        sessions = []
        for session_model in session_models:
            # 분석 결과 파싱
            analysis = None
            if session_model.analysis_json:
                analysis = json.loads(session_model.analysis_json)

            sessions.append(ConsultSession(
                id=session_model.id,
                user_id=session_model.user_id,
                mbti=MBTI(session_model.mbti),
                gender=Gender(session_model.gender),
                created_at=session_model.created_at,
                messages=[],  # 히스토리에서는 메시지 로드 안함
                completed=True,
                analysis=analysis,
            ))

        return sessions
