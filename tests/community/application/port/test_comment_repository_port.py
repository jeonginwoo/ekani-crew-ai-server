from abc import ABC

from app.community.application.port.comment_repository_port import CommentRepositoryPort


class TestCommentRepositoryPort:
    """CommentRepositoryPort 인터페이스 테스트"""

    def test_is_abstract_class(self):
        """CommentRepositoryPort는 추상 클래스이다"""
        assert issubclass(CommentRepositoryPort, ABC)

    def test_has_save_method(self):
        """save 메서드가 정의되어 있다"""
        assert hasattr(CommentRepositoryPort, "save")

    def test_has_find_by_post_id_method(self):
        """find_by_post_id 메서드가 정의되어 있다"""
        assert hasattr(CommentRepositoryPort, "find_by_post_id")

    def test_has_count_by_post_id_method(self):
        """count_by_post_id 메서드가 정의되어 있다"""
        assert hasattr(CommentRepositoryPort, "count_by_post_id")
