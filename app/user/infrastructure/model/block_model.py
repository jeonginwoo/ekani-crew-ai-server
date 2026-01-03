import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base


class BlockModel(Base):
    """차단 ORM 모델"""

    __tablename__ = "blocks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    blocker_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    blocked_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False)

    # Relationships
    blocker = relationship("UserModel", foreign_keys=[blocker_id])
    blocked = relationship("UserModel", foreign_keys=[blocked_id])
