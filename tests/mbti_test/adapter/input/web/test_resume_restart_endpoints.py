"""
MBTI-5 기능 테스트: 이어하기 / 새로하기
"""
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, MagicMock
import uuid
from datetime import datetime
from app.auth.adapter.input.web.auth_dependency import get_current_user_id
from app.mbti_test.domain.mbti_test_session import MBTITestSession, TestType, TestStatus, Turn
from app.mbti_test.domain.mbti_message import MBTIMessage, MessageRole, MessageSource

client = TestClient(app)

def mock_get_current_user_id():
    return str(uuid.uuid4())

app.dependency_overrides[get_current_user_id] = mock_get_current_user_id


def test_resume_endpoint_with_in_progress_test():
    """이어하기: 진행 중인 테스트가 있으면 세션과 다음 질문 반환"""
    with patch("app.mbti_test.application.use_case.resume_test_use_case.ResumeTestUseCase.execute") as mock_resume:
        # 실제 도메인 객체 사용
        session_id = uuid.uuid4()
        user_id = uuid.uuid4()

        # 이전 대화 내용 (2개의 턴)
        turns = [
            Turn(
                turn_number=1,
                question="질문 1",
                answer="답변 1",
                dimension="EI",
                scores={"E": 5, "I": 3},
                side="E",
                score=5
            ),
            Turn(
                turn_number=2,
                question="질문 2",
                answer="답변 2",
                dimension="SN",
                scores={"S": 4, "N": 6},
                side="N",
                score=6
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
            content="다음 질문입니다",
            source=MessageSource.HUMAN,
        )

        mock_resume.return_value = MagicMock(
            session=mock_session,
            next_question=mock_next_question
        )

        response = client.post("/mbti-test/resume")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "resumed"
        assert "session" in data
        assert "messages" in data  # 이전 대화 메시지 리스트
        assert "next_question" in data
        # 메시지 개수 확인 (2개 턴 = 4개 메시지: 질문1, 답변1, 질문2, 답변2)
        assert len(data["messages"]) == 4
        assert data["messages"][0]["role"] == "assistant"
        assert data["messages"][0]["content"] == "질문 1"
        assert data["messages"][1]["role"] == "user"
        assert data["messages"][1]["content"] == "답변 1"


def test_resume_endpoint_without_in_progress_test():
    """이어하기: 진행 중인 테스트가 없으면 404 반환"""
    with patch("app.mbti_test.application.use_case.resume_test_use_case.ResumeTestUseCase.execute") as mock_resume:
        mock_resume.return_value = None

        response = client.post("/mbti-test/resume")

        assert response.status_code == 404
        assert "진행 중인 테스트" in response.json()["detail"]


def test_restart_endpoint_creates_new_test():
    """새로하기: 기존 세션을 삭제하고 새 테스트 시작"""
    with patch("app.mbti_test.application.use_case.delete_in_progress_test_use_case.DeleteInProgressTestUseCase.execute") as mock_delete:
        with patch("app.mbti_test.application.use_case.start_mbti_test_service.StartMBTITestService") as mock_start:
            mock_session = MagicMock()
            mock_session.id = uuid.uuid4()
            mock_first_question = MagicMock()
            mock_start.return_value.execute.return_value = MagicMock(
                session=mock_session,
                first_question=mock_first_question
            )

            response = client.post("/mbti-test/restart")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "restarted"
            assert "session" in data
            assert "first_question" in data
            mock_delete.assert_called_once()


def test_restart_endpoint_deletes_existing_session():
    """새로하기: 기존 세션이 있어도 삭제하고 새로 시작"""
    with patch("app.mbti_test.application.use_case.delete_in_progress_test_use_case.DeleteInProgressTestUseCase.execute") as mock_delete:
        with patch("app.mbti_test.application.use_case.start_mbti_test_service.StartMBTITestService") as mock_start:
            mock_session = MagicMock()
            mock_session.id = uuid.uuid4()
            mock_first_question = MagicMock()
            mock_start.return_value.execute.return_value = MagicMock(
                session=mock_session,
                first_question=mock_first_question
            )

            response = client.post("/mbti-test/restart")

            # 항상 기존 세션 삭제를 시도해야 함
            assert mock_delete.call_count == 1
            assert response.status_code == 200
