import pytest
from unittest.mock import AsyncMock, patch
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.auth.adapter.input.web.auth_dependency import get_current_user_id
from app.auth.domain.session import Session


@pytest.fixture
def app():
    """테스트용 FastAPI 앱"""
    test_app = FastAPI()

    @test_app.get("/protected")
    async def protected_route(user_id: str = Depends(get_current_user_id)):
        return {"user_id": user_id}

    return test_app


@pytest.fixture
def client(app):
    """테스트 클라이언트"""
    return TestClient(app)


class TestAuthDependency:
    """인증 의존성 테스트"""

    def test_유효한_세션으로_user_id_반환(self, client):
        """유효한 세션 ID 쿠키면 user_id를 반환한다"""
        # Given: 유효한 세션
        session = Session(session_id="valid-session-123", user_id="user-456")

        with patch(
            "app.auth.adapter.input.web.auth_dependency.RedisSessionRepository"
        ) as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo.find_by_session_id.return_value = session
            mock_repo_class.return_value = mock_repo

            # When: session_id 쿠키로 요청
            response = client.get(
                "/protected",
                cookies={"session_id": "valid-session-123"},
            )

            # Then: user_id 반환
            assert response.status_code == 200
            assert response.json()["user_id"] == "user-456"

    def test_세션_없이_요청시_401_에러(self, client):
        """session_id 쿠키 없이 요청하면 401 에러"""
        response = client.get("/protected")

        assert response.status_code == 401
        assert "인증" in response.json()["detail"]

    def test_유효하지_않은_세션으로_요청시_401_에러(self, client):
        """존재하지 않는 세션 ID면 401 에러"""
        with patch(
            "app.auth.adapter.input.web.auth_dependency.RedisSessionRepository"
        ) as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo.find_by_session_id.return_value = None
            mock_repo_class.return_value = mock_repo

            response = client.get(
                "/protected",
                cookies={"session_id": "invalid-session-999"},
            )

            assert response.status_code == 401
            assert "세션" in response.json()["detail"]