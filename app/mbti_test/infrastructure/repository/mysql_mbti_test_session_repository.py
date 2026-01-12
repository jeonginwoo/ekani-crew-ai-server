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

        # Turn 객체들을 명시적으로 딕셔너리로 변환
        answers_data = []
        for turn in session.turns:
            turn_dict = {
                "turn_number": turn.turn_number,
                "question": turn.question,
                "answer": turn.answer,
                "dimension": turn.dimension,
                "scores": turn.scores,
                "side": turn.side,
                "score": turn.score,
            }
            answers_data.append(turn_dict)

        print(f"[DB SAVE] Saving session {session.id} with {len(answers_data)} turns")
        if answers_data:
            print(f"[DB SAVE] First turn: question='{answers_data[0]['question'][:30] if answers_data[0]['question'] else 'EMPTY'}...', answer='{answers_data[0]['answer'][:30] if answers_data[0]['answer'] else 'EMPTY'}...'")

        if model is None:
            model = MBTITestSessionModel(
                id=str(session.id),
                user_id=str(session.user_id),
                status=session.status.value,
                answers=answers_data,
                greeting_completed=session.greeting_completed,
                pending_question=session.pending_question,
                pending_question_dimension=session.pending_question_dimension,
            )
            self.db.add(model)
        else:
            model.status = session.status.value
            model.answers = answers_data
            model.greeting_completed = session.greeting_completed
            model.pending_question = session.pending_question
            model.pending_question_dimension = session.pending_question_dimension

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
        for i, answer_data in enumerate(model.answers or []):
            question_text = ""
            # For human questions, we can retrieve the question text
            if i < len(selected_human_questions):
                question_text = selected_human_questions[i]
            # For AI questions, the question should be in the answer_data
            else:
                question_text = answer_data.get("question", "")

            answer_text = answer_data.get("answer")
            if answer_text is None:
                answer_text = answer_data.get("content", "")

            turns.append(Turn(
                turn_number=answer_data.get("turn_number", i + 1),
                question=question_text,
                answer=answer_text,
                dimension=answer_data.get("dimension", ""),
                scores=answer_data.get("scores", {}),
                side=answer_data.get("side", ""),
                score=answer_data.get("score", 0),
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
            current_question_index=len(turns),
            pending_question=model.pending_question,
            pending_question_dimension=model.pending_question_dimension,
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
        for i, answer_data in enumerate(model.answers or []):
            question_text = ""
            # For human questions, we can retrieve the question text
            if i < len(selected_human_questions):
                question_text = selected_human_questions[i]
            # For AI questions, the question should be in the answer_data
            else:
                question_text = answer_data.get("question", "")

            answer_text = answer_data.get("answer")
            if answer_text is None:
                answer_text = answer_data.get("content", "")

            turn = Turn(
                turn_number=answer_data.get("turn_number", i + 1),
                question=question_text,
                answer=answer_text,
                dimension=answer_data.get("dimension", ""),
                scores=answer_data.get("scores", {}),
                side=answer_data.get("side", ""),
                score=answer_data.get("score", 0),
            )
            turns.append(turn)

        return MBTITestSession(
            id=uuid.UUID(model.id),
            user_id=uuid.UUID(model.user_id),
            test_type=TestType.HUMAN,
            status=TestStatus(model.status),
            created_at=model.created_at,
            turns=turns,
            selected_human_questions=selected_human_questions,
            greeting_completed=model.greeting_completed,
            current_question_index=len(turns),
            pending_question=model.pending_question,
            pending_question_dimension=model.pending_question_dimension,
        )


    def add_answer(self, session_id: uuid.UUID, turn: Turn) -> None:
        model = self.db.query(MBTITestSessionModel).filter(
            MBTITestSessionModel.id == str(session_id)
        ).first()

        if model:
            # Turn 객체를 명시적으로 딕셔너리로 변환
            turn_dict = {
                "turn_number": turn.turn_number,
                "question": turn.question,
                "answer": turn.answer,
                "dimension": turn.dimension,
                "scores": turn.scores,
                "side": turn.side,
                "score": turn.score,
            }

            print(f"[DB SAVE] Saving turn {turn.turn_number}:")
            print(f"  - question: '{turn.question[:50] if turn.question else 'EMPTY'}...'")
            print(f"  - answer: '{turn.answer[:50] if turn.answer else 'EMPTY'}...'")
            print(f"  - turn_dict: {turn_dict}")

            answers = list(model.answers or [])
            answers.append(turn_dict)
            model.answers = answers
            self.db.commit()

            print(f"[DB SAVE] Committed. Total answers now: {len(model.answers)}")

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

        from app.mbti_test.infrastructure.service.human_question_provider import HumanQuestionProvider
        human_question_provider = HumanQuestionProvider()
        selected_human_questions = human_question_provider.select_random_questions(seed=str(model.id))

        turns = []
        for i, answer_data in enumerate(model.answers or []):
            question_text = ""
            if i < len(selected_human_questions):
                question_text = selected_human_questions[i]
            else:
                question_text = answer_data.get("question", "")

            answer_text = answer_data.get("answer")
            if answer_text is None:
                answer_text = answer_data.get("content", "")

            turns.append(Turn(
                turn_number=answer_data.get("turn_number", i + 1),
                question=question_text,
                answer=answer_text,
                dimension=answer_data.get("dimension", ""),
                scores=answer_data.get("scores", {}),
                side=answer_data.get("side", ""),
                score=answer_data.get("score", 0),
            ))

        return MBTITestSessionExtended(
            id=model.id,
            user_id=model.user_id,
            status=status,
            answers=list(model.answers or []),
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
