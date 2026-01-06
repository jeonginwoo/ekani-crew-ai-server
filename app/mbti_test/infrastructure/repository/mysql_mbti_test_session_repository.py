import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.mbti_test.application.port.output.mbti_test_session_repository import MBTITestSessionRepositoryPort
from app.mbti_test.domain.mbti_test_session import MBTITestSession, TestStatus, TestType, Turn
from app.mbti_test.domain.mbti_result import MBTIResult, MBTITestSessionExtended, SessionStatus
from app.mbti_test.infrastructure.mbti_test_models import MBTITestSessionModel


class MySQLMBTITestSessionRepository(MBTITestSessionRepositoryPort):
    def __init__(self, db: Session):
        self.db = db

    def save(self, session: MBTITestSession) -> MBTITestSession:
        model = self.db.query(MBTITestSessionModel).filter(
            MBTITestSessionModel.id == str(session.id)
        ).first()

        if model is None:
            model = MBTITestSessionModel(
                id=str(session.id),
                user_id=str(session.user_id),
                status=session.status.value,
                answers=[turn.__dict__ for turn in session.turns],
                greeting_completed=session.greeting_completed,
            )
            self.db.add(model)
        else:
            model.status = session.status.value
            model.answers = [turn.__dict__ for turn in session.turns]
            model.greeting_completed = session.greeting_completed

        self.db.commit()
        self.db.refresh(model)
        return session

    def delete(self, session: MBTITestSession):
        model = self.db.query(MBTITestSessionModel).filter(
            MBTITestSessionModel.id == str(session.id)
        ).first()
        if model:
            self.db.delete(model)
            self.db.commit()

    def find_by_id(self, session_id: uuid.UUID) -> MBTITestSession | None:
        model = self.db.query(MBTITestSessionModel).filter(
            MBTITestSessionModel.id == str(session_id)
        ).first()

        if model is None:
            return None

        from app.mbti_test.infrastructure.service.human_question_provider import HumanQuestionProvider
        human_question_provider = HumanQuestionProvider()
        selected_human_questions = human_question_provider.select_random_questions(seed=str(model.id))

        # Reconstruct turns from answers
        turns = []
        for i, answer in enumerate(model.answers or []):
            turns.append(Turn(
                turn_number=i + 1,
                question=answer.get("question", ""),
                answer=answer.get("content", ""),
                dimension=answer.get("dimension", ""),
                scores=answer.get("scores", {}),
                side=answer.get("side", ""),
                score=answer.get("score", 0),
            ))

        return MBTITestSession(
            id=uuid.UUID(model.id),
            user_id=uuid.UUID(model.user_id),
            test_type=TestType.HUMAN,
            status=TestStatus(model.status),
            created_at=model.created_at,
            turns=turns,
            selected_human_questions=selected_human_questions,
            greeting_completed=model.greeting_completed,
            current_question_index=len(turns)
        )


    def find_by_user_id_and_status(self, user_id: str, status: str) -> MBTITestSession | None:
        model = self.db.query(MBTITestSessionModel).filter(
            MBTITestSessionModel.user_id == user_id,
            MBTITestSessionModel.status == status
        ).first()

        if model is None:
            return None

        from app.mbti_test.infrastructure.service.human_question_provider import HumanQuestionProvider
        human_question_provider = HumanQuestionProvider()
        selected_human_questions = human_question_provider.select_random_questions(seed=str(model.id))

        # Reconstruct turns from answers
        turns = []
        for i, answer in enumerate(model.answers or []):
            turns.append(Turn(
                turn_number=i + 1,
                question=answer.get("question", ""),
                answer=answer.get("content", ""),
                dimension=answer.get("dimension", ""),
                scores=answer.get("scores", {}),
                side=answer.get("side", ""),
                score=answer.get("score", 0),
            ))

        return MBTITestSession(
            id=uuid.UUID(model.id),
            user_id=uuid.UUID(model.user_id),
            test_type=TestType.HUMAN,
            status=TestStatus(model.status),
            created_at=model.created_at,
            turns=turns,
            selected_human_questions=selected_human_questions,
            greeting_completed=model.greeting_completed,
            current_question_index=len(turns)
        )


    def add_answer(self, session_id: uuid.UUID, turn: Turn) -> None:
        model = self.db.query(MBTITestSessionModel).filter(
            MBTITestSessionModel.id == str(session_id)
        ).first()

        if model:
            answers = list(model.answers or [])
            answers.append(turn.__dict__)
            model.answers = answers
            self.db.commit()

    def find_extended_by_id(self, session_id: uuid.UUID) -> MBTITestSessionExtended | None:
        model = self.db.query(MBTITestSessionModel).filter(
            MBTITestSessionModel.id == str(session_id)
        ).first()

        if model is None:
            return None

        status = SessionStatus.COMPLETED if model.status == "COMPLETED" else SessionStatus.IN_PROGRESS

        result = None
        if model.result_mbti:
            result = MBTIResult(
                mbti=model.result_mbti,
                dimension_scores=model.result_dimension_scores or {},
                timestamp=model.result_timestamp or datetime.now(timezone.utc),
            )

        return MBTITestSessionExtended(
            id=model.id,
            user_id=model.user_id,
            status=status,
            turns=[Turn(**turn) for turn in (model.answers or [])],
            result=result,
        )

    def save_result_and_complete(self, session_id: uuid.UUID, result: MBTIResult) -> None:
        model = self.db.query(MBTITestSessionModel).filter(
            MBTITestSessionModel.id == str(session_id)
        ).first()

        if model:
            model.status = "COMPLETED"
            model.result_mbti = result.mbti
            model.result_dimension_scores = result.dimension_scores
            model.result_timestamp = result.timestamp
            self.db.commit()