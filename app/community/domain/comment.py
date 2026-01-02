from datetime import datetime


class Comment:
    """댓글 도메인 엔티티"""

    def __init__(
        self,
        id: str,
        post_id: str,
        author_id: str,
        content: str,
        created_at: datetime | None = None,
    ):
        self.id = id
        self.post_id = post_id
        self.author_id = author_id
        self.content = content
        self.created_at = created_at or datetime.now()
