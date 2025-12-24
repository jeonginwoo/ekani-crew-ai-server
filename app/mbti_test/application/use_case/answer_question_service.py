import uuid
from typing import List

from app.mbti_test.application.port.input.answer_question_use_case import (
    AnswerQuestionCommand,
    AnswerQuestionResponse,
    AnswerQuestionUseCase,
)
from app.mbti_test.application.port.output.mbti_test_session_repository import MBTITestSessionRepositoryPort
from app.mbti_test.application.port.ai_question_provider_port import AIQuestionProviderPort
from app.mbti_test.infrastructure.service.human_question_provider import HumanQuestionProvider
from app.mbti_test.domain.mbti_message import MBTIMessage, MessageRole, MessageSource
from app.mbti_test.domain.mbti_test_session import TestStatus
from app.mbti_test.domain.models import GenerateAIQuestionCommand, ChatMessage, MessageRole as ModelMessageRole


HUMAN_QUESTION_COUNT = 12
TOTAL_QUESTION_COUNT = 24


class AnswerQuestionService(AnswerQuestionUseCase):
    def __init__(
        self,
        session_repository: MBTITestSessionRepositoryPort,
        human_question_provider: HumanQuestionProvider,
        ai_question_provider: AIQuestionProviderPort,
    ):
        self._session_repository = session_repository
        self._human_question_provider = human_question_provider
        self._ai_question_provider = ai_question_provider

    def execute(self, command: AnswerQuestionCommand) -> AnswerQuestionResponse:
        # 1. Find session
        session = self._session_repository.find_by_id(uuid.UUID(command.session_id))
        if not session:
            raise ValueError(f"Session not found: {command.session_id}")

        # 2. 인사 응답 처리 (greeting 후 첫 답변)
        if not session.greeting_completed:
            # 인사에 대한 응답은 저장 안 함 (무시)
            session.greeting_completed = True

            # 첫 번째 질문 반환 (index 0)
            first_question = self._human_question_provider.get_question_from_list(
                0, session.selected_human_questions
            )

            # 질문 히스토리에 저장
            if first_question:
                session.questions.append(first_question.content)

            self._session_repository.save(session)

            return AnswerQuestionResponse(
                question_number=1,  # 1번 질문
                total_questions=TOTAL_QUESTION_COUNT,
                next_question=first_question,
                is_completed=False,
            )

        # 3. 정상 답변 처리 - 답변 저장 및 인덱스 증가
        session.answers.append({"content": command.answer})
        session.current_question_index += 1

        current_index = session.current_question_index

        # 4. 완료 체크
        if current_index >= TOTAL_QUESTION_COUNT:
            session.status = TestStatus.COMPLETED
            self._session_repository.save(session)
            return AnswerQuestionResponse(
                question_number=current_index,
                total_questions=TOTAL_QUESTION_COUNT,
                next_question=None,
                is_completed=True,
            )

        # 5. 다음 질문 가져오기
        if current_index < HUMAN_QUESTION_COUNT:
            # Human phase (questions 0-11) - 세션에 저장된 랜덤 선택 질문 사용
            next_question = self._human_question_provider.get_question_from_list(
                current_index, session.selected_human_questions
            )
        else:
            # AI phase (questions 12-23)
            history = self._build_chat_history(session)
            ai_turn = current_index - HUMAN_QUESTION_COUNT + 1  # 1-12 for AI

            ai_command = GenerateAIQuestionCommand(
                session_id=command.session_id,
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
                # Fallback if AI fails
                next_question = MBTIMessage(
                    role=MessageRole.ASSISTANT,
                    content="다음 질문입니다: 당신의 성격을 한 단어로 표현한다면?",
                    source=MessageSource.AI,
                )

        # 6. 질문 히스토리에 저장
        if next_question:
            session.questions.append(next_question.content)

        self._session_repository.save(session)

        return AnswerQuestionResponse(
            question_number=current_index + 1,  # 1-based for display
            total_questions=TOTAL_QUESTION_COUNT,
            next_question=next_question,
            is_completed=False,
        )

    def _build_chat_history(self, session) -> List[ChatMessage]:
        """Build chat history from session for AI context"""
        history = []

        # Interleave questions and answers
        for i, question in enumerate(session.questions):
            history.append(ChatMessage(
                role=ModelMessageRole.ASSISTANT,
                content=question,
            ))
            if i < len(session.answers):
                history.append(ChatMessage(
                    role=ModelMessageRole.USER,
                    content=session.answers[i].get("content", ""),
                ))

        return history