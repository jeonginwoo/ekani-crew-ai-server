import pytest
from unittest.mock import AsyncMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.user.adapter.input.web.user_router import user_router, get_user_repository
from app.user.domain.user import User
from app.auth.domain.session import Session
from tests.user.fixtures.fake_user_repository import FakeUserRepository


@pytest.fixture
def user_repo():
    return FakeUserRepository()


@pytest.fixture
def app(user_repo):
    app = FastAPI()
    app.include_router(user_router, prefix="/user")
    app.dependency_overrides[get_user_repository] = lambda: user_repo
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


def mock_session(session: Session):
    """세션 인증을 모킹하는 컨텍스트 매니저"""
    mock_repo = AsyncMock()
    mock_repo.find_by_session_id.return_value = session
    return patch(
        "app.auth.adapter.input.web.auth_dependency.RedisSessionRepository",
        return_value=mock_repo
    )


def test_update_profile_success_with_cookie(client, user_repo):
    user = User(id="user-123", email="test@example.com")
    user_repo.save(user)
    session = Session(session_id="valid-session", user_id="user-123")

    with mock_session(session):
        response = client.put(
            "/user/profile",
            cookies={"session_id": "valid-session"},
            json={"mbti": "intj", "gender": "male"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["mbti_test"] == "INTJ"
    assert data["gender"] == "MALE"


def test_update_profile_with_different_gender(client, user_repo):
    user = User(id="user-123", email="test@example.com")
    user_repo.save(user)
    session = Session(session_id="valid-session", user_id="user-123")

    with mock_session(session):
        response = client.put(
            "/user/profile",
            cookies={"session_id": "valid-session"},
            json={"mbti": "intj", "gender": "female"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["mbti_test"] == "INTJ"
    assert data["gender"] == "FEMALE"


def test_update_profile_requires_auth(client):
    response = client.put(
        "/user/profile",
        json={"mbti": "INTJ", "gender": "MALE"},
    )
    assert response.status_code == 401


def test_update_profile_user_not_found_returns_404(client):
    session = Session(session_id="valid-session", user_id="missing-user")

    with mock_session(session):
        response = client.put(
            "/user/profile",
            cookies={"session_id": "valid-session"},
            json={"mbti": "INTJ", "gender": "MALE"},
        )

    assert response.status_code == 404


def test_update_profile_invalid_mbti_returns_400(client, user_repo):
    user = User(id="user-123", email="test@example.com")
    user_repo.save(user)
    session = Session(session_id="valid-session", user_id="user-123")

    with mock_session(session):
        response = client.put(
            "/user/profile",
            cookies={"session_id": "valid-session"},
            json={"mbti": "XXXX", "gender": "MALE"},
        )

    assert response.status_code == 400


def test_get_profile_success(client, user_repo):
    user = User(id="user-123", email="test@example.com")
    user_repo.save(user)
    session = Session(session_id="valid-session", user_id="user-123")

    with mock_session(session):
        response = client.get(
            "/user/profile",
            cookies={"session_id": "valid-session"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "user-123"
    assert data["email"] == "test@example.com"
    assert data["mbti_test"] is None
    assert data["gender"] is None


def test_get_profile_requires_auth(client):
    response = client.get("/user/profile")
    assert response.status_code == 401


def test_get_profile_user_not_found_returns_404(client):
    session = Session(session_id="valid-session", user_id="missing-user")

    with mock_session(session):
        response = client.get(
            "/user/profile",
            cookies={"session_id": "valid-session"},
        )

    assert response.status_code == 404