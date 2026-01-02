import pytest

from app.community.application.use_case.add_comment_use_case import AddCommentUseCase
from app.community.domain.post import Post, PostType
from tests.community.fixtures.fake_comment_repository import FakeCommentRepository
from tests.community.fixtures.fake_post_repository import FakePostRepository


class TestAddCommentUseCase:
    """AddCommentUseCase 테스트"""

    def setup_method(self):
        self.comment_repository = FakeCommentRepository()
        self.post_repository = FakePostRepository()
        self.use_case = AddCommentUseCase(
            comment_repository=self.comment_repository,
            post_repository=self.post_repository,
        )

    def test_add_comment_to_post(self):
        """게시글에 댓글을 추가할 수 있다"""
        # Given
        post = Post(
            id="post-1",
            author_id="user-1",
            title="INTJ 남자 원래 이런가요?",
            content="INTJ 남친이 답장을 안 해요...",
            post_type=PostType.FREE,
        )
        self.post_repository.save(post)

        # When
        comment_id = self.use_case.execute(
            post_id="post-1",
            author_id="user-2",
            content="저도 INTJ인데 공감돼요",
        )

        # Then
        assert comment_id is not None
        comments = self.comment_repository.find_by_post_id("post-1")
        assert len(comments) == 1
        assert comments[0].content == "저도 INTJ인데 공감돼요"
        assert comments[0].author_id == "user-2"

    def test_add_comment_raises_error_when_post_not_found(self):
        """존재하지 않는 게시글에 댓글을 달면 에러가 발생한다"""
        # When & Then
        with pytest.raises(ValueError, match="게시글을 찾을 수 없습니다"):
            self.use_case.execute(
                post_id="non-existent-post",
                author_id="user-1",
                content="댓글 내용",
            )

    def test_add_multiple_comments_to_same_post(self):
        """같은 게시글에 여러 댓글을 추가할 수 있다"""
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
        self.use_case.execute(
            post_id="post-1", author_id="user-2", content="첫 번째 댓글"
        )
        self.use_case.execute(
            post_id="post-1", author_id="user-3", content="두 번째 댓글"
        )

        # Then
        comments = self.comment_repository.find_by_post_id("post-1")
        assert len(comments) == 2
