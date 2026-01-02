from datetime import datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.community.adapter.input.web.post_router import (
    post_router,
    get_post_repository,
    get_comment_repository,
    get_user_repository,
)
from app.community.domain.comment import Comment
from app.community.domain.post import Post, PostType
from app.shared.vo.gender import Gender
from app.shared.vo.mbti import MBTI
from app.user.domain.user import User
from tests.community.fixtures.fake_comment_repository import FakeCommentRepository
from tests.community.fixtures.fake_post_repository import FakePostRepository
from tests.user.fixtures.fake_user_repository import FakeUserRepository


@pytest.fixture
def fake_post_repository():
    return FakePostRepository()


@pytest.fixture
def fake_comment_repository():
    return FakeCommentRepository()


@pytest.fixture
def fake_user_repository():
    return FakeUserRepository()


@pytest.fixture
def client(fake_post_repository, fake_comment_repository, fake_user_repository):
    app = FastAPI()
    app.include_router(post_router, prefix="/community")

    def override_post_repository():
        return fake_post_repository

    def override_comment_repository():
        return fake_comment_repository

    def override_user_repository():
        return fake_user_repository

    app.dependency_overrides[get_post_repository] = override_post_repository
    app.dependency_overrides[get_comment_repository] = override_comment_repository
    app.dependency_overrides[get_user_repository] = override_user_repository
    return TestClient(app)


class TestCommentRouter:
    """Comment API 라우터 테스트"""

    def test_create_comment(
        self, client, fake_post_repository, fake_comment_repository
    ):
        """게시글에 댓글을 작성할 수 있다"""
        # Given
        post = Post(
            id="post-1",
            author_id="user-1",
            title="테스트 게시글",
            content="내용",
            post_type=PostType.FREE,
        )
        fake_post_repository.save(post)

        # When
        response = client.post(
            "/community/posts/post-1/comments",
            json={
                "author_id": "user-2",
                "content": "저도 INTJ인데 공감돼요",
            },
        )

        # Then
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["content"] == "저도 INTJ인데 공감돼요"
        assert data["author_id"] == "user-2"

    def test_create_comment_post_not_found(self, client):
        """존재하지 않는 게시글에 댓글 작성 시 404를 반환한다"""
        response = client.post(
            "/community/posts/non-existent/comments",
            json={
                "author_id": "user-1",
                "content": "댓글 내용",
            },
        )

        assert response.status_code == 404

    def test_get_comments(
        self,
        client,
        fake_post_repository,
        fake_comment_repository,
        fake_user_repository,
    ):
        """게시글의 댓글 목록을 조회할 수 있다"""
        # Given
        post = Post(
            id="post-1",
            author_id="user-1",
            title="테스트 게시글",
            content="내용",
            post_type=PostType.FREE,
        )
        fake_post_repository.save(post)

        user = User(
            id="user-2",
            email="user2@test.com",
            mbti=MBTI("INTJ"),
            gender=Gender("MALE"),
        )
        fake_user_repository.save(user)

        comment = Comment(
            id="comment-1",
            post_id="post-1",
            author_id="user-2",
            content="저도 INTJ인데 공감돼요",
            created_at=datetime(2025, 1, 1, 12, 0, 0),
        )
        fake_comment_repository.save(comment)

        # When
        response = client.get("/community/posts/post-1/comments")

        # Then
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["content"] == "저도 INTJ인데 공감돼요"
        assert data["items"][0]["author_mbti"] == "INTJ"

    def test_get_comments_post_not_found(self, client):
        """존재하지 않는 게시글의 댓글 조회 시 404를 반환한다"""
        response = client.get("/community/posts/non-existent/comments")

        assert response.status_code == 404

    def test_get_comments_sorted_by_time(
        self,
        client,
        fake_post_repository,
        fake_comment_repository,
        fake_user_repository,
    ):
        """댓글을 시간순으로 정렬하여 반환한다"""
        # Given
        post = Post(
            id="post-1",
            author_id="user-1",
            title="테스트 게시글",
            content="내용",
            post_type=PostType.FREE,
        )
        fake_post_repository.save(post)

        user2 = User(
            id="user-2",
            email="user2@test.com",
            mbti=MBTI("ENFP"),
        )
        user3 = User(
            id="user-3",
            email="user3@test.com",
            mbti=MBTI("ISTP"),
        )
        fake_user_repository.save(user2)
        fake_user_repository.save(user3)

        comment1 = Comment(
            id="comment-1",
            post_id="post-1",
            author_id="user-2",
            content="첫 번째 댓글",
            created_at=datetime(2025, 1, 1, 12, 0, 0),
        )
        comment2 = Comment(
            id="comment-2",
            post_id="post-1",
            author_id="user-3",
            content="두 번째 댓글",
            created_at=datetime(2025, 1, 1, 14, 0, 0),
        )
        fake_comment_repository.save(comment1)
        fake_comment_repository.save(comment2)

        # When
        response = client.get("/community/posts/post-1/comments")

        # Then
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["items"][0]["id"] == "comment-1"
        assert data["items"][1]["id"] == "comment-2"