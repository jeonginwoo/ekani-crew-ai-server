from fastapi import APIRouter, Depends, HTTPException, status, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uuid

from app.auth.adapter.input.web.auth_dependency import get_current_user_id
from app.user.application.port.user_repository_port import UserRepositoryPort
from app.user.application.port.block_repository_port import BlockRepositoryPort
from app.chat.application.port.chat_room_repository_port import ChatRoomRepositoryPort
from app.user.application.use_case.block_user_use_case import BlockUserUseCase, BlockUserUseCaseImpl
from app.chat.application.use_case.deactivate_chat_room_use_case import DeactivateChatRoomUseCase
from app.user.domain.user import User
from app.shared.vo.mbti import MBTI
from app.shared.vo.gender import Gender
from app.user.infrastructure.repository.mysql_user_repository import MySQLUserRepository
from app.user.infrastructure.repository.mysql_block_repository import MySQLBlockRepository
from app.chat.infrastructure.repository.mysql_chat_room_repository import MySQLChatRoomRepository
from config.database import get_db

user_router = APIRouter()


def get_user_repository(db: Session = Depends(get_db)) -> UserRepositoryPort:
    return MySQLUserRepository(db)


def get_block_repository(db: Session = Depends(get_db)) -> BlockRepositoryPort:
    return MySQLBlockRepository(db)


def get_chat_room_repository(db: Session = Depends(get_db)) -> ChatRoomRepositoryPort:
    return MySQLChatRoomRepository(db)


def get_deactivate_chat_room_use_case(
    chat_room_repo: ChatRoomRepositoryPort = Depends(get_chat_room_repository)
) -> DeactivateChatRoomUseCase:
    return DeactivateChatRoomUseCase(chat_room_repository=chat_room_repo)


def get_block_user_use_case(
    block_repo: BlockRepositoryPort = Depends(get_block_repository),
    user_repo: UserRepositoryPort = Depends(get_user_repository),
    deactivate_use_case: DeactivateChatRoomUseCase = Depends(get_deactivate_chat_room_use_case)
) -> BlockUserUseCase:
    return BlockUserUseCaseImpl(
        block_repository=block_repo,
        user_repository=user_repo,
        deactivate_chat_room_use_case=deactivate_use_case
    )


class UpdateProfileRequest(BaseModel):
    mbti: str
    gender: str


@user_router.post("/{blocked_user_id}/block", status_code=status.HTTP_204_NO_CONTENT)
def block_user(
    blocked_user_id: str,
    blocker_id: str = Depends(get_current_user_id),
    use_case: BlockUserUseCase = Depends(get_block_user_use_case)
):
    """특정 유저를 차단한다"""
    if blocker_id == blocked_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="자기 자신을 차단할 수 없습니다",
        )

    try:
        # The use case expects UUID objects
        use_case.block(blocker_id=uuid.UUID(blocker_id), blocked_id=uuid.UUID(blocked_user_id))
    except ValueError as e:
        # This could be a user not found error from the use case
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@user_router.get("/profile")
def get_profile(
    user_id: str = Depends(get_current_user_id),
    user_repo: UserRepositoryPort = Depends(get_user_repository),
):
    """현재 로그인한 사용자의 프로필 조회"""
    user = user_repo.find_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다",
        )

    return {
        "id": user.id,
        "email": user.email,
        "mbti": user.mbti.value if user.mbti else None,
        "gender": user.gender.value if user.gender else None,
    }


@user_router.put("/profile")
def update_profile(
    request: UpdateProfileRequest,
    user_id: str = Depends(get_current_user_id),
    user_repo: UserRepositoryPort = Depends(get_user_repository),
):
    """MBTI/성별 프로필 저장 (upsert)"""
    user = user_repo.find_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다",
        )

    try:
        mbti = MBTI(request.mbti)
        gender = Gender(request.gender.upper())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    updated_user = User(
        id=user.id,
        email=user.email,
        mbti=mbti,
        gender=gender,
    )
    user_repo.save(updated_user)

    return {
        "id": updated_user.id,
        "email": updated_user.email,
        "mbti": updated_user.mbti.value,
        "gender": updated_user.gender.value,
    }