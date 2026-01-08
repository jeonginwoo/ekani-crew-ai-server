"""
Test to verify that /resume endpoint returns messages correctly
"""
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch
import uuid
from datetime import datetime
from app.auth.adapter.input.web.auth_dependency import get_current_user_id
from app.mbti_test.domain.mbti_test_session import MBTITestSession, TestType, TestStatus, Turn
from app.mbti_test.domain.mbti_message import MBTIMessage, MessageRole, MessageSource
from app.mbti_test.application.use_case.resume_test_use_case import ResumeTestResult

client = TestClient(app)

def mock_get_current_user_id():
    return str(uuid.uuid4())

app.dependency_overrides[get_current_user_id] = mock_get_current_user_id


def test_resume_returns_messages_from_turns():
    """
    /resume 엔드포인트가 turns로부터 messages를 생성해서 반환하는지 테스트
    """
    with patch("app.mbti_test.application.use_case.resume_test_use_case.ResumeTestUseCase.execute") as mock_resume:
        # Given: 2개 턴이 있는 진행 중인 세션
        session_id = uuid.uuid4()
        user_id = uuid.uuid4()

        turns = [
            Turn(
                turn_number=1,
                question="첫 번째 질문입니다",
                answer="첫 번째 답변입니다",
                dimension="EI",
                scores={"E": 6, "I": 4},
                side="E",
                score=6
            ),
            Turn(
                turn_number=2,
                question="두 번째 질문입니다",
                answer="두 번째 답변입니다",
                dimension="SN",
                scores={"S": 3, "N": 7},
                side="N",
                score=7
            )
        ]

        mock_session = MBTITestSession(
            id=session_id,
            user_id=user_id,
            test_type=TestType.HUMAN,
            status=TestStatus.IN_PROGRESS,
            created_at=datetime.now(),
            turns=turns,
            current_question_index=2,
            greeting_completed=True,
        )

        mock_next_question = MBTIMessage(
            role=MessageRole.ASSISTANT,
            content="세 번째 질문입니다",
            source=MessageSource.HUMAN,
        )

        mock_resume.return_value = ResumeTestResult(
            session=mock_session,
            next_question=mock_next_question
        )

        # When: /resume 엔드포인트 호출
        response = client.post("/mbti-test/resume")

        # Then: 200 OK
        print(f"\nResponse status: {response.status_code}")
        print(f"Response data: {response.json()}")

        assert response.status_code == 200
        data = response.json()

        # messages 필드가 존재하는지 확인
        assert "messages" in data, f"messages field should be present in response. Got: {data.keys()}"

        # messages가 올바르게 변환되었는지 확인
        messages = data["messages"]
        assert len(messages) == 4, "Should have 4 messages (2 turns * 2 messages)"

        # 첫 번째 턴
        assert messages[0]["role"] == "assistant"
        assert messages[0]["content"] == "첫 번째 질문입니다"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "첫 번째 답변입니다"

        # 두 번째 턴
        assert messages[2]["role"] == "assistant"
        assert messages[2]["content"] == "두 번째 질문입니다"
        assert messages[3]["role"] == "user"
        assert messages[3]["content"] == "두 번째 답변입니다"

        # next_question도 확인
        assert data["next_question"]["content"] == "세 번째 질문입니다"

        print(f"[PASS] Test passed: messages correctly returned from /resume")
        print(f"Messages: {messages}")


def test_resume_with_empty_turns():
    """
    턴이 없는 경우에도 messages가 빈 배열로 반환되는지 테스트
    """
    with patch("app.mbti_test.application.use_case.resume_test_use_case.ResumeTestUseCase.execute") as mock_resume:
        # Given: 턴이 없는 세션 (greeting만 완료)
        session_id = uuid.uuid4()
        user_id = uuid.uuid4()

        mock_session = MBTITestSession(
            id=session_id,
            user_id=user_id,
            test_type=TestType.HUMAN,
            status=TestStatus.IN_PROGRESS,
            created_at=datetime.now(),
            turns=[],  # 빈 턴
            current_question_index=0,
            greeting_completed=True,
        )

        mock_next_question = MBTIMessage(
            role=MessageRole.ASSISTANT,
            content="첫 번째 질문입니다",
            source=MessageSource.HUMAN,
        )

        mock_resume.return_value = ResumeTestResult(
            session=mock_session,
            next_question=mock_next_question
        )

        # When: /resume 엔드포인트 호출
        response = client.post("/mbti-test/resume")

        # Then: messages는 빈 배열
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert len(data["messages"]) == 0

        print(f"[PASS] Test passed: empty turns returns empty messages")
