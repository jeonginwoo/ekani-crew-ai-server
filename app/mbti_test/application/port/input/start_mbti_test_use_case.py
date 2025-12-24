import uuid
from abc import ABC, abstractmethod
from pydantic import BaseModel

from app.mbti_test.domain.mbti_message import MBTIMessage
from app.mbti_test.domain.mbti_test_session import MBTITestSession, TestType


class StartMBTITestCommand(BaseModel):
    user_id: uuid.UUID
    test_type: TestType = TestType.HUMAN  # 항상 human 12개 + AI 12개 순서


class StartMBTITestResponse(BaseModel):
    session: MBTITestSession
    first_question: MBTIMessage


class StartMBTITestUseCase(ABC):
    @abstractmethod
    def execute(self, command: StartMBTITestCommand) -> StartMBTITestResponse:
        pass
