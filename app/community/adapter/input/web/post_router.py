import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.community.application.port.comment_repository_port import CommentRepositoryPort
from app.community.application.port.post_repository_port import PostRepositoryPort
from app.community.application.use_case.add_comment_use_case import AddCommentUseCase
from app.community.application.use_case.get_comments_use_case import (
    GetCommentsUseCase,
)
from app.community.domain.post import Post, PostType
from app.community.infrastructure.repository.mysql_comment_repository import (
    MySQLCommentRepository,
)
from app.community.infrastructure.repository.mysql_post_repository import (
    MySQLPostRepository,
)
from app.user.application.port.user_repository_port import UserRepositoryPort
from app.user.infrastructure.repository.mysql_user_repository import (
    MySQLUserRepository,
)
from config.database import get_db


post_router = APIRouter()


def get_post_repository(db: Session = Depends(get_db)) -> PostRepositoryPort:
    return MySQLPostRepository(db)


def get_comment_repository(db: Session = Depends(get_db)) -> CommentRepositoryPort:
    return MySQLCommentRepository(db)


def get_user_repository(db: Session = Depends(get_db)) -> UserRepositoryPort:
    return MySQLUserRepository(db)


class CreatePostRequest(BaseModel):
    author_id: str
    title: str
    content: str
    post_type: str  # "topic" or "free"
    topic_id: str | None = None


class PostResponse(BaseModel):
    id: str
    author_id: str
    title: str
    content: str
    post_type: str
    topic_id: str | None
    created_at: datetime


@post_router.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(
    request: CreatePostRequest,
    post_repo: PostRepositoryPort = Depends(get_post_repository),
) -> PostResponse:
    """게시글 작성"""
    post_type = PostType.TOPIC if request.post_type == "topic" else PostType.FREE

    post = Post(
        id=str(uuid.uuid4()),
        author_id=request.author_id,
        title=request.title,
        content=request.content,
        post_type=post_type,
        topic_id=request.topic_id,
    )
    post_repo.save(post)

    return PostResponse(
        id=post.id,
        author_id=post.author_id,
        title=post.title,
        content=post.content,
        post_type=post.post_type.value,
        topic_id=post.topic_id,
        created_at=post.created_at,
    )


class PostListResponse(BaseModel):
    items: list[PostResponse]
    total: int
    page: int
    size: int


@post_router.get("/posts")
def get_posts(
    type: str | None = None,
    page: int = 1,
    size: int = 10,
    post_repo: PostRepositoryPort = Depends(get_post_repository),
) -> PostListResponse:
    """게시글 목록 조회 (필터링, 페이지네이션)"""
    post_type = None
    if type:
        post_type = PostType.TOPIC if type == "topic" else PostType.FREE

    posts = post_repo.find_paginated(page=page, size=size, post_type=post_type)

    if post_type:
        total = post_repo.count_by_post_type(post_type)
    else:
        total = post_repo.count_all()

    items = [
        PostResponse(
            id=post.id,
            author_id=post.author_id,
            title=post.title,
            content=post.content,
            post_type=post.post_type.value,
            topic_id=post.topic_id,
            created_at=post.created_at,
        )
        for post in posts
    ]

    return PostListResponse(items=items, total=total, page=page, size=size)


@post_router.get("/posts/{post_id}")
def get_post(
    post_id: str,
    post_repo: PostRepositoryPort = Depends(get_post_repository),
) -> PostResponse:
    """게시글 상세 조회 (SEO용 고유 URL)"""
    post = post_repo.find_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다",
        )

    return PostResponse(
        id=post.id,
        author_id=post.author_id,
        title=post.title,
        content=post.content,
        post_type=post.post_type.value,
        topic_id=post.topic_id,
        created_at=post.created_at,
    )


# ================= Comment Endpoints =================


class CreateCommentRequest(BaseModel):
    author_id: str
    content: str


class CommentResponse(BaseModel):
    id: str
    post_id: str
    author_id: str
    author_mbti: str | None
    content: str
    created_at: datetime


class CommentListResponse(BaseModel):
    items: list[CommentResponse]


@post_router.post("/posts/{post_id}/comments", status_code=status.HTTP_201_CREATED)
def create_comment(
    post_id: str,
    request: CreateCommentRequest,
    post_repo: PostRepositoryPort = Depends(get_post_repository),
    comment_repo: CommentRepositoryPort = Depends(get_comment_repository),
) -> CommentResponse:
    """댓글 작성"""
    use_case = AddCommentUseCase(
        comment_repository=comment_repo,
        post_repository=post_repo,
    )

    try:
        comment_id = use_case.execute(
            post_id=post_id,
            author_id=request.author_id,
            content=request.content,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return CommentResponse(
        id=comment_id,
        post_id=post_id,
        author_id=request.author_id,
        author_mbti=None,
        content=request.content,
        created_at=datetime.now(),
    )


@post_router.get("/posts/{post_id}/comments")
def get_comments(
    post_id: str,
    post_repo: PostRepositoryPort = Depends(get_post_repository),
    comment_repo: CommentRepositoryPort = Depends(get_comment_repository),
    user_repo: UserRepositoryPort = Depends(get_user_repository),
) -> CommentListResponse:
    """게시글 댓글 목록 조회"""
    use_case = GetCommentsUseCase(
        comment_repository=comment_repo,
        post_repository=post_repo,
        user_repository=user_repo,
    )

    try:
        comments = use_case.execute(post_id=post_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    items = [
        CommentResponse(
            id=comment.id,
            post_id=comment.post_id,
            author_id=comment.author_id,
            author_mbti=comment.author_mbti,
            content=comment.content,
            created_at=comment.created_at,
        )
        for comment in comments
    ]

    return CommentListResponse(items=items)
