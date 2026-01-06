from app.chat.application.port.block_repository_port import BlockRepositoryPort
from app.chat.domain.block import Block


class FakeBlockRepository(BlockRepositoryPort):
    """테스트용 Fake Block 저장소"""

    def __init__(self):
        self._blocks: dict[str, Block] = {}

    def save(self, block: Block) -> None:
        """차단을 저장한다"""
        self._blocks[block.id] = block

    def find_by_id(self, block_id: str) -> Block | None:
        """id로 차단을 조회한다"""
        return self._blocks.get(block_id)

    async def find_by_blocker_and_blocked(self, blocker_id: str, blocked_user_id: str) -> Block | None:
        """특정 차단 관계를 조회한다"""
        for block in self._blocks.values():
            if block.blocker_id == blocker_id and block.blocked_user_id == blocked_user_id:
                return block
        return None

    def delete(self, block: Block) -> None:
        """차단을 삭제한다"""
        if block.id in self._blocks:
            del self._blocks[block.id]

    def get_blocked_user_ids(self, blocker_id: str) -> list[str]:
        """차단한 유저 id 목록을 조회한다"""
        return [
            block.blocked_user_id for block in self._blocks.values()
            if block.blocker_id == blocker_id
        ]

    def get_blocker_ids(self, blocked_user_id: str) -> list[str]:
        """나를 차단한 유저 id 목록을 조회한다"""
        return [
            block.blocker_id for block in self._blocks.values()
            if block.blocked_user_id == blocked_user_id
        ]
