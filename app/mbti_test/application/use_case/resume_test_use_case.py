import uuid
from typing import List
from pydantic import BaseModel, ConfigDict

from app.mbti_test.application.port.output.mbti_test_session_repository import MBTITestSessionRepositoryPort
from app.mbti_test.application.port.ai_question_provider_port import AIQuestionProviderPort
from app.mbti_test.infrastructure.service.human_question_provider import HumanQuestionProvider
from app.mbti_test.domain.mbti_message import MBTIMessage, MessageRole, MessageSource
from app.mbti_test.domain.mbti_test_session import MBTITestSession
from app.mbti_test.domain.models import (
    GenerateAIQuestionCommand,
    ChatMessage,
    MessageRole as ModelMessageRole,
)

HUMAN_QUESTION_COUNT = 12
TOTAL_QUESTION_COUNT = 24

class ResumeTestResponse(BaseModel):
    session: MBTITestSession
    next_question: MBTIMessage | None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ResumeTestUseCase:
    def __init__(
        self,
        session_repository: MBTITestSessionRepositoryPort,
        human_question_provider: HumanQuestionProvider,
        ai_question_provider: AIQuestionProviderPort,
    ):
        self._session_repository = session_repository
        self._human_question_provider = human_question_provider
        self._ai_question_provider = ai_question_provider

    def execute(self, user_id: str) -> ResumeTestResponse | None:
        session = self._session_repository.find_by_user_id_and_status(user_id, "IN_PROGRESS")
        if not session:
            return None

        session.selected_human_questions = self._human_question_provider.select_random_questions(
            seed=str(session.id)
        )
        session.current_question_index = len(session.turns)

        next_question: MBTIMessage | None

        if not session.greeting_completed:
            next_question = self._human_question_provider.get_greeting()
        else:
            current_index = session.current_question_index
            if current_index >= TOTAL_QUESTION_COUNT:
                next_question = None
            elif current_index < HUMAN_QUESTION_COUNT:
                next_question = self._human_question_provider.get_question_from_list(
                    current_index, session.selected_human_questions
                )
            else:
                history = self._build_chat_history(session)
                ai_turn = current_index - HUMAN_QUESTION_COUNT + 1
                ai_command = GenerateAIQuestionCommand(
                    session_id=str(session.id),
                    turn=ai_turn,
                    history=history,
                    question_mode="normal",
                )
                ai_response = self._ai_question_provider.generate_questions(ai_command)
                if ai_response.questions:
                    next_question = MBTIMessage(
                        role=MessageRole.ASSISTANT,
                        content=ai_response.questions[0].text,
                        source=MessageSource.AI,
                    )
                else:
                    next_question = MBTIMessage(
                        role=MessageRole.ASSISTANT,
                        content="다음 질문입니다: 당신의 성격을 한 단어로 표현한다면?",
                        source=MessageSource.AI,
                    )
        
        return ResumeTestResponse(session=session, next_question=next_question)

    def _build_chat_history(self, session) -> List[ChatMessage]:
        history = []
        for turn in session.turns:
            history.append(ChatMessage(
                role=ModelMessageRole.ASSISTANT,
                content=turn.question,
            ))
            history.append(ChatMessage(
                role=ModelMessageRole.USER,
                content=turn.answer,
            ))
        return history
