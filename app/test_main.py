import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """DB 연결 없이 테스트하기 위해 lifespan을 모킹"""
    with patch('config.database.engine') as mock_engine:
        with patch('config.database.Base') as mock_base:
            mock_engine.dispose = MagicMock()
            from app.main import app
            with TestClient(app) as c:
                yield c


class TestHealthEndpoint:
    def test_health_endpoint_returns_ok(self, client):
        """/health 엔드포인트 정상 응답"""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"