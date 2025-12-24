import uuid
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.mbti_test.adapter.input.web.mbti_router import mbti_router
from app.auth.domain.session import Session


@pytest.fixture
def app():
    """테스트용 FastAPI 앱"""
    app = FastAPI()
    app.include_router(mbti_router, prefix="/mbti-test")
    return app


@pytest.fixture
def client(app):
    """테스트 클라이언트"""
    return TestClient(app)


def mock_session(session: Session):
    """세션 인증을 모킹하는 컨텍스트 매니저"""
    mock_repo = AsyncMock()
    mock_repo.find_by_session_id.return_value = session
    return patch(
        "app.auth.adapter.input.web.auth_dependency.RedisSessionRepository",
        return_value=mock_repo
    )


def test_start_mbti_test_endpoint(client: TestClient):
    # Given
    user_id = uuid.uuid4()
    session = Session(session_id="valid-session", user_id=str(user_id))

    # When
    with mock_session(session):
        response = client.post(
            "/mbti-test/start?test_type=ai",
            cookies={"session_id": "valid-session"}
        )

    # Then
    assert response.status_code == 200
    response_json = response.json()
    assert "session" in response_json
    assert "first_question" in response_json


def test_start_mbti_test_without_auth_returns_401(client: TestClient):
    # When
    response = client.post("/mbti-test/start?test_type=ai")

    # Then
    assert response.status_code == 401