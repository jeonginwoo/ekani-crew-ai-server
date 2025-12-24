
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict

class TestType(Enum):
    HUMAN = "human"
    AI = "ai"

class TestStatus(Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

@dataclass
class MBTITestSession:
    id: uuid.UUID
    user_id: uuid.UUID
    test_type: TestType
    status: TestStatus
    created_at: datetime
    questions: List[str] = field(default_factory=list)  # 질문 히스토리
    answers: List[Dict] = field(default_factory=list)
    current_question_index: int = 0
    selected_human_questions: List[str] = field(default_factory=list)  # 세션 시작 시 랜덤 선택된 12개 질문
    greeting_completed: bool = False  # 인사 응답 완료 여부
