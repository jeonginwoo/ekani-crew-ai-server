from app.community.application.port.comment_repository_port import CommentRepositoryPort
from app.community.domain.comment import Comment


class FakeCommentRepository(CommentRepositoryPort):
    """테스트용 Fake 댓글 저장소"""

    def __init__(self):
        self._comments: dict[str, Comment] = {}

    def save(self, comment: Comment) -> None:
        self._comments[comment.id] = comment

    def find_by_post_id(self, post_id: str) -> list[Comment]:
        comments = [c for c in self._comments.values() if c.post_id == post_id]
        return sorted(comments, key=lambda c: c.created_at)

    def count_by_post_id(self, post_id: str) -> int:
        return len([c for c in self._comments.values() if c.post_id == post_id])
