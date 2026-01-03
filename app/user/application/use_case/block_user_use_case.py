import uuid
from abc import ABC, abstractmethod

from app.user.application.port.block_repository_port import BlockRepositoryPort
from app.user.application.port.user_repository_port import UserRepositoryPort
from app.chat.application.use_case.deactivate_chat_room_use_case import DeactivateChatRoomUseCase
from app.user.domain.block import Block


class BlockUserUseCase(ABC):
    @abstractmethod
    def block(self, blocker_id: uuid.UUID, blocked_id: uuid.UUID) -> None:
        pass


class BlockUserUseCaseImpl(BlockUserUseCase):
    def __init__(
        self,
        block_repository: BlockRepositoryPort,
        user_repository: UserRepositoryPort,
        deactivate_chat_room_use_case: DeactivateChatRoomUseCase
    ):
        self.block_repository = block_repository
        self.user_repository = user_repository
        self.deactivate_chat_room_use_case = deactivate_chat_room_use_case

    def block(self, blocker_id: uuid.UUID, blocked_id: uuid.UUID) -> None:
        blocker = self.user_repository.find_by_id(str(blocker_id))
        blocked = self.user_repository.find_by_id(str(blocked_id))

        if not blocker or not blocked:
            raise ValueError("User not found")

        existing_block = self.block_repository.find_by_blocker_and_blocked(
            blocker_id=str(blocker_id), blocked_user_id=str(blocked_id)
        )

        if existing_block:
            return

        new_block = Block(blocker_id=blocker_id, blocked_id=blocked_id)
        self.block_repository.save(new_block)

        # Deactivate chat room between the two users
        self.deactivate_chat_room_use_case.execute(user1_id=blocker_id, user2_id=blocked_id)
