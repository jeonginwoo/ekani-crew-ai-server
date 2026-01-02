import uuid

from app.community.application.port.comment_repository_port import CommentRepositoryPort
from app.community.application.port.post_repository_port import PostRepositoryPort
from app.community.domain.comment import Comment


class AddCommentUseCase:
    """댓글 작성 유스케이스"""

    def __init__(
        self,
        comment_repository: CommentRepositoryPort,
        post_repository: PostRepositoryPort,
    ):
        self._comment_repository = comment_repository
        self._post_repository = post_repository

    def execute(self, post_id: str, author_id: str, content: str) -> str:
        """게시글에 댓글을 추가하고 comment_id를 반환한다"""
        # 게시글 존재 여부 확인
        post = self._post_repository.find_by_id(post_id)
        if post is None:
            raise ValueError("게시글을 찾을 수 없습니다")

        # 댓글 생성 및 저장
        comment = Comment(
            id=str(uuid.uuid4()),
            post_id=post_id,
            author_id=author_id,
            content=content,
        )
        self._comment_repository.save(comment)

        return comment.id
