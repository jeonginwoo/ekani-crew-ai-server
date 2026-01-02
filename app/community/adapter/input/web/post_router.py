import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.community.application.port.post_repository_port import PostRepositoryPort
from app.community.domain.post import Post, PostType
from app.community.infrastructure.repository.mysql_post_repository import MySQLPostRepository
from config.database import get_db


post_router = APIRouter()


def get_post_repository(db: Session = Depends(get_db)) -> PostRepositoryPort:
    return MySQLPostRepository(db)


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
