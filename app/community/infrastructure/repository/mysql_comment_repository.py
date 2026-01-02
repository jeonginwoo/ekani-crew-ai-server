from sqlalchemy.orm import Session

from app.community.application.port.comment_repository_port import CommentRepositoryPort
from app.community.domain.comment import Comment
from app.community.infrastructure.model.comment_model import CommentModel


class MySQLCommentRepository(CommentRepositoryPort):
    """MySQL 기반 댓글 저장소"""

    def __init__(self, db_session: Session):
        self._db = db_session

    def save(self, comment: Comment) -> None:
        """댓글을 저장한다"""
        comment_model = CommentModel(
            id=comment.id,
            post_id=comment.post_id,
            author_id=comment.author_id,
            content=comment.content,
            created_at=comment.created_at,
        )
        self._db.merge(comment_model)
        self._db.commit()

    def find_by_post_id(self, post_id: str) -> list[Comment]:
        """게시글 ID로 댓글 목록을 조회한다 (시간순 정렬)"""
        comment_models = (
            self._db.query(CommentModel)
            .filter(CommentModel.post_id == post_id)
            .order_by(CommentModel.created_at)
            .all()
        )

        return [self._to_domain(m) for m in comment_models]

    def count_by_post_id(self, post_id: str) -> int:
        """게시글 ID로 댓글 수를 조회한다"""
        return (
            self._db.query(CommentModel)
            .filter(CommentModel.post_id == post_id)
            .count()
        )

    def _to_domain(self, model: CommentModel) -> Comment:
        """ORM 모델을 도메인 객체로 변환한다"""
        return Comment(
            id=model.id,
            post_id=model.post_id,
            author_id=model.author_id,
            content=model.content,
            created_at=model.created_at,
        )