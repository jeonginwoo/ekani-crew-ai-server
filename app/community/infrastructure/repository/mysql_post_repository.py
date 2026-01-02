from sqlalchemy.orm import Session

from app.community.application.port.post_repository_port import PostRepositoryPort
from app.community.domain.post import Post, PostType
from app.community.infrastructure.model.post_model import PostModel


class MySQLPostRepository(PostRepositoryPort):
    """MySQL 기반 게시글 저장소"""

    def __init__(self, db_session: Session):
        self._db = db_session

    def save(self, post: Post) -> None:
        """게시글을 저장한다 (insert 또는 update)"""
        post_model = PostModel(
            id=post.id,
            author_id=post.author_id,
            title=post.title,
            content=post.content,
            post_type=post.post_type.value,
            topic_id=post.topic_id,
            created_at=post.created_at,
        )
        self._db.merge(post_model)
        self._db.commit()

    def find_by_id(self, post_id: str) -> Post | None:
        """id로 게시글을 조회한다"""
        post_model = self._db.query(PostModel).filter(
            PostModel.id == post_id
        ).first()

        if post_model is None:
            return None

        return self._to_domain(post_model)

    def find_all(self) -> list[Post]:
        """모든 게시글을 최신순으로 조회한다"""
        post_models = self._db.query(PostModel).order_by(
            PostModel.created_at.desc()
        ).all()

        return [self._to_domain(m) for m in post_models]

    def find_by_post_type(self, post_type: PostType) -> list[Post]:
        """게시글 유형별로 조회한다"""
        post_models = self._db.query(PostModel).filter(
            PostModel.post_type == post_type.value
        ).order_by(PostModel.created_at.desc()).all()

        return [self._to_domain(m) for m in post_models]

    def count_all(self) -> int:
        """전체 게시글 수를 반환한다"""
        return self._db.query(PostModel).count()

    def count_by_post_type(self, post_type: PostType) -> int:
        """게시글 유형별 개수를 반환한다"""
        return self._db.query(PostModel).filter(
            PostModel.post_type == post_type.value
        ).count()

    def find_paginated(
        self,
        page: int,
        size: int,
        post_type: PostType | None = None,
    ) -> list[Post]:
        """페이지네이션된 게시글 목록을 조회한다"""
        query = self._db.query(PostModel)

        if post_type:
            query = query.filter(PostModel.post_type == post_type.value)

        offset = (page - 1) * size
        post_models = query.order_by(
            PostModel.created_at.desc()
        ).offset(offset).limit(size).all()

        return [self._to_domain(m) for m in post_models]

    def _to_domain(self, model: PostModel) -> Post:
        """ORM 모델을 도메인 객체로 변환한다"""
        post_type = PostType.TOPIC if model.post_type == "topic" else PostType.FREE
        return Post(
            id=model.id,
            author_id=model.author_id,
            title=model.title,
            content=model.content,
            post_type=post_type,
            topic_id=model.topic_id,
            created_at=model.created_at,
        )
