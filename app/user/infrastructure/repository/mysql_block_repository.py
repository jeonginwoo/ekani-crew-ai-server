from sqlalchemy.orm import Session
from app.user.application.port.block_repository_port import BlockRepositoryPort
from app.user.domain.block import Block
from app.user.infrastructure.model.block_model import BlockModel


class MySQLBlockRepository(BlockRepositoryPort):
    """MySQL 기반 차단 저장소"""

    def __init__(self, db_session: Session):
        self._db = db_session

    def save(self, block: Block) -> None:
        """차단을 저장한다"""
        block_model = self._to_model(block)
        self._db.merge(block_model)

    def find_by_id(self, block_id: str) -> Block | None:
        """id로 차단을 조회한다"""
        block_model = self._db.query(BlockModel).filter(BlockModel.id == block_id).first()
        return self._to_domain(block_model) if block_model else None

    async def find_by_blocker_and_blocked(self, blocker_id: str, blocked_user_id: str) -> Block | None:
        """특정 차단 관계를 조회한다"""
        block_model = self._db.query(BlockModel).filter(
            BlockModel.blocker_id == blocker_id,
            BlockModel.blocked_id == blocked_user_id
        ).first()
        return self._to_domain(block_model) if block_model else None

    def delete(self, block: Block) -> None:
        """차단을 삭제한다"""
        block_model = self._db.query(BlockModel).filter(BlockModel.id == str(block.id)).first()
        if block_model:
            self._db.delete(block_model)

    def get_blocked_user_ids(self, blocker_id: str) -> list[str]:
        """차단한 유저 id 목록을 조회한다"""
        results = self._db.query(BlockModel.blocked_id).filter(BlockModel.blocker_id == blocker_id).all()
        return [str(result[0]) for result in results]

    def get_blocker_ids(self, blocked_user_id: str) -> list[str]:
        """나를 차단한 유저 id 목록을 조회한다"""
        results = self._db.query(BlockModel.blocker_id).filter(BlockModel.blocked_id == blocked_user_id).all()
        return [str(result[0]) for result in results]

    def _to_domain(self, model: BlockModel) -> Block:
        return Block(
            id=model.id,
            blocker_id=model.blocker_id,
            blocked_id=model.blocked_id,
            created_at=model.created_at
        )

    def _to_model(self, domain: Block) -> BlockModel:
        return BlockModel(
            id=str(domain.id),
            blocker_id=str(domain.blocker_id),
            blocked_id=str(domain.blocked_id),
            created_at=domain.created_at
        )
