import uuid

from app.chat.application.port.chat_room_repository_port import ChatRoomRepositoryPort


class DeactivateChatRoomUseCase:
    def __init__(self, chat_room_repository: ChatRoomRepositoryPort):
        self.chat_room_repository = chat_room_repository

    def execute(self, user1_id: uuid.UUID, user2_id: uuid.UUID) -> None:
        room = self.chat_room_repository.find_by_users(str(user1_id), str(user2_id))
        if room and room.status == "active":
            room.deactivate_by_block()
            self.chat_room_repository.save(room)
