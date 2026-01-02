from dataclasses import dataclass
from datetime import datetime

from app.community.application.port.comment_repository_port import CommentRepositoryPort
from app.community.application.port.post_repository_port import PostRepositoryPort
from app.user.application.port.user_repository_port import UserRepositoryPort


@dataclass
class CommentWithAuthorMBTI:
    """작성자 MBTI를 포함한 댓글 정보"""

    id: str
    post_id: str
    author_id: str
    author_mbti: str | None
    content: str
    created_at: datetime


class GetCommentsUseCase:
    """댓글 목록 조회 유스케이스"""

    def __init__(
        self,
        comment_repository: CommentRepositoryPort,
        post_repository: PostRepositoryPort,
        user_repository: UserRepositoryPort,
    ):
        self._comment_repository = comment_repository
        self._post_repository = post_repository
        self._user_repository = user_repository

    def execute(self, post_id: str) -> list[CommentWithAuthorMBTI]:
        """게시글의 댓글 목록을 작성자 MBTI와 함께 조회한다"""
        # 게시글 존재 여부 확인
        post = self._post_repository.find_by_id(post_id)
        if post is None:
            raise ValueError("게시글을 찾을 수 없습니다")

        # 댓글 조회 (시간순 정렬됨)
        comments = self._comment_repository.find_by_post_id(post_id)

        # 작성자 MBTI 정보 조회 및 결과 생성
        result = []
        for comment in comments:
            user = self._user_repository.find_by_id(comment.author_id)
            author_mbti = user.mbti.value if user and user.mbti else None

            result.append(
                CommentWithAuthorMBTI(
                    id=comment.id,
                    post_id=comment.post_id,
                    author_id=comment.author_id,
                    author_mbti=author_mbti,
                    content=comment.content,
                    created_at=comment.created_at,
                )
            )

        return result
