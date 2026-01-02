from datetime import datetime

import pytest

from app.community.application.use_case.get_comments_use_case import (
    CommentWithAuthorMBTI,
    GetCommentsUseCase,
)
from app.community.domain.comment import Comment
from app.community.domain.post import Post, PostType
from app.user.domain.user import User
from app.shared.vo.mbti import MBTI
from app.shared.vo.gender import Gender
from tests.community.fixtures.fake_comment_repository import FakeCommentRepository
from tests.community.fixtures.fake_post_repository import FakePostRepository
from tests.user.fixtures.fake_user_repository import FakeUserRepository


class TestGetCommentsUseCase:
    """GetCommentsUseCase 테스트"""

    def setup_method(self):
        self.comment_repository = FakeCommentRepository()
        self.post_repository = FakePostRepository()
        self.user_repository = FakeUserRepository()
        self.use_case = GetCommentsUseCase(
            comment_repository=self.comment_repository,
            post_repository=self.post_repository,
            user_repository=self.user_repository,
        )

    def _create_user(self, user_id: str, mbti_str: str) -> User:
        return User(
            id=user_id,
            email=f"{user_id}@test.com",
            gender=Gender("MALE"),
            mbti=MBTI(mbti_str),
        )

    def test_get_comments_with_author_mbti(self):
        """댓글 목록을 작성자 MBTI와 함께 조회할 수 있다"""
        # Given
        post = Post(
            id="post-1",
            author_id="user-1",
            title="테스트 게시글",
            content="내용",
            post_type=PostType.FREE,
        )
        self.post_repository.save(post)

        user = self._create_user("user-2", "INTJ")
        self.user_repository.save(user)

        comment = Comment(
            id="comment-1",
            post_id="post-1",
            author_id="user-2",
            content="저도 INTJ인데 공감돼요",
            created_at=datetime(2025, 1, 1, 12, 0, 0),
        )
        self.comment_repository.save(comment)

        # When
        result = self.use_case.execute(post_id="post-1")

        # Then
        assert len(result) == 1
        assert isinstance(result[0], CommentWithAuthorMBTI)
        assert result[0].id == "comment-1"
        assert result[0].content == "저도 INTJ인데 공감돼요"
        assert result[0].author_id == "user-2"
        assert result[0].author_mbti == "INTJ"

    def test_get_comments_raises_error_when_post_not_found(self):
        """존재하지 않는 게시글의 댓글을 조회하면 에러가 발생한다"""
        with pytest.raises(ValueError, match="게시글을 찾을 수 없습니다"):
            self.use_case.execute(post_id="non-existent-post")

    def test_get_comments_returns_empty_list_when_no_comments(self):
        """댓글이 없으면 빈 리스트를 반환한다"""
        # Given
        post = Post(
            id="post-1",
            author_id="user-1",
            title="테스트 게시글",
            content="내용",
            post_type=PostType.FREE,
        )
        self.post_repository.save(post)

        # When
        result = self.use_case.execute(post_id="post-1")

        # Then
        assert result == []

    def test_get_comments_sorted_by_created_at(self):
        """댓글을 시간순으로 정렬하여 반환한다"""
        # Given
        post = Post(
            id="post-1",
            author_id="user-1",
            title="테스트 게시글",
            content="내용",
            post_type=PostType.FREE,
        )
        self.post_repository.save(post)

        user2 = self._create_user("user-2", "ENFP")
        user3 = self._create_user("user-3", "ISTP")
        self.user_repository.save(user2)
        self.user_repository.save(user3)

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
        self.comment_repository.save(comment1)
        self.comment_repository.save(comment2)

        # When
        result = self.use_case.execute(post_id="post-1")

        # Then
        assert len(result) == 2
        assert result[0].id == "comment-1"
        assert result[1].id == "comment-2"

    def test_get_comments_with_unknown_user(self):
        """사용자 정보가 없으면 MBTI를 None으로 반환한다"""
        # Given
        post = Post(
            id="post-1",
            author_id="user-1",
            title="테스트 게시글",
            content="내용",
            post_type=PostType.FREE,
        )
        self.post_repository.save(post)

        comment = Comment(
            id="comment-1",
            post_id="post-1",
            author_id="unknown-user",
            content="댓글 내용",
            created_at=datetime(2025, 1, 1, 12, 0, 0),
        )
        self.comment_repository.save(comment)

        # When
        result = self.use_case.execute(post_id="post-1")

        # Then
        assert len(result) == 1
        assert result[0].author_mbti is None