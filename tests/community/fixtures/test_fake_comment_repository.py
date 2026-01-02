from datetime import datetime

from app.community.application.port.comment_repository_port import CommentRepositoryPort
from app.community.domain.comment import Comment
from tests.community.fixtures.fake_comment_repository import FakeCommentRepository


class TestFakeCommentRepository:
    """FakeCommentRepository 테스트"""

    def setup_method(self):
        self.repository = FakeCommentRepository()

    def test_is_comment_repository_port(self):
        """CommentRepositoryPort를 구현한다"""
        assert isinstance(self.repository, CommentRepositoryPort)

    def test_save_and_find_by_post_id(self):
        """댓글을 저장하고 게시글 ID로 조회할 수 있다"""
        comment = Comment(
            id="comment-1",
            post_id="post-1",
            author_id="user-1",
            content="첫 번째 댓글",
            created_at=datetime(2025, 1, 1, 12, 0, 0),
        )
        self.repository.save(comment)

        comments = self.repository.find_by_post_id("post-1")

        assert len(comments) == 1
        assert comments[0].id == "comment-1"
        assert comments[0].content == "첫 번째 댓글"

    def test_find_by_post_id_returns_empty_list_when_no_comments(self):
        """댓글이 없으면 빈 리스트를 반환한다"""
        comments = self.repository.find_by_post_id("non-existent-post")

        assert comments == []

    def test_find_by_post_id_returns_comments_sorted_by_created_at(self):
        """댓글을 시간순으로 정렬하여 반환한다"""
        comment1 = Comment(
            id="comment-1",
            post_id="post-1",
            author_id="user-1",
            content="첫 번째 댓글",
            created_at=datetime(2025, 1, 1, 12, 0, 0),
        )
        comment2 = Comment(
            id="comment-2",
            post_id="post-1",
            author_id="user-2",
            content="두 번째 댓글",
            created_at=datetime(2025, 1, 1, 14, 0, 0),
        )
        comment3 = Comment(
            id="comment-3",
            post_id="post-1",
            author_id="user-3",
            content="세 번째 댓글",
            created_at=datetime(2025, 1, 1, 13, 0, 0),
        )
        self.repository.save(comment1)
        self.repository.save(comment2)
        self.repository.save(comment3)

        comments = self.repository.find_by_post_id("post-1")

        assert len(comments) == 3
        assert comments[0].id == "comment-1"
        assert comments[1].id == "comment-3"
        assert comments[2].id == "comment-2"

    def test_count_by_post_id(self):
        """게시글 ID로 댓글 수를 조회한다"""
        comment1 = Comment(
            id="comment-1", post_id="post-1", author_id="user-1", content="댓글 1"
        )
        comment2 = Comment(
            id="comment-2", post_id="post-1", author_id="user-2", content="댓글 2"
        )
        comment3 = Comment(
            id="comment-3", post_id="post-2", author_id="user-1", content="다른 게시글 댓글"
        )
        self.repository.save(comment1)
        self.repository.save(comment2)
        self.repository.save(comment3)

        count = self.repository.count_by_post_id("post-1")

        assert count == 2

    def test_count_by_post_id_returns_zero_when_no_comments(self):
        """댓글이 없으면 0을 반환한다"""
        count = self.repository.count_by_post_id("non-existent-post")

        assert count == 0
