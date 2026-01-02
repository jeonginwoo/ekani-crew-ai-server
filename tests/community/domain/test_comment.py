from datetime import datetime

from app.community.domain.comment import Comment


class TestComment:
    """Comment 도메인 엔티티 테스트"""

    def test_create_comment(self):
        """댓글을 생성할 수 있다"""
        comment = Comment(
            id="comment-1",
            post_id="post-1",
            author_id="user-1",
            content="저도 INTJ인데 공감돼요",
        )

        assert comment.id == "comment-1"
        assert comment.post_id == "post-1"
        assert comment.author_id == "user-1"
        assert comment.content == "저도 INTJ인데 공감돼요"
        assert isinstance(comment.created_at, datetime)

    def test_create_comment_with_created_at(self):
        """생성 시간을 지정하여 댓글을 생성할 수 있다"""
        created_at = datetime(2025, 1, 1, 12, 0, 0)
        comment = Comment(
            id="comment-2",
            post_id="post-1",
            author_id="user-2",
            content="좋은 글이에요",
            created_at=created_at,
        )

        assert comment.created_at == created_at