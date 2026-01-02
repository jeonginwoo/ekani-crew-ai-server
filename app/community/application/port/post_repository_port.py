from abc import ABC, abstractmethod

from app.community.domain.post import Post, PostType


class PostRepositoryPort(ABC):
    """게시글 저장소 포트"""

    @abstractmethod
    def save(self, post: Post) -> None:
        """게시글을 저장한다"""
        pass

    @abstractmethod
    def find_by_id(self, post_id: str) -> Post | None:
        """id로 게시글을 조회한다"""
        pass

    @abstractmethod
    def find_all(self) -> list[Post]:
        """모든 게시글을 최신순으로 조회한다"""
        pass

    @abstractmethod
    def find_by_post_type(self, post_type: PostType) -> list[Post]:
        """게시글 유형별로 조회한다"""
        pass

    @abstractmethod
    def count_all(self) -> int:
        """전체 게시글 수를 반환한다"""
        pass

    @abstractmethod
    def count_by_post_type(self, post_type: PostType) -> int:
        """게시글 유형별 개수를 반환한다"""
        pass

    @abstractmethod
    def find_paginated(
        self,
        page: int,
        size: int,
        post_type: PostType | None = None,
    ) -> list[Post]:
        """페이지네이션된 게시글 목록을 조회한다"""
        pass
