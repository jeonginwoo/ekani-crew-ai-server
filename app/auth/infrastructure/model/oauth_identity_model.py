import uuid

from sqlalchemy import Column, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from config.database import Base


class OAuthIdentityModel(Base):
    """OAuth Identity ORM 모델"""

    __tablename__ = "user_identities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    provider = Column(String(20), nullable=False)  # google, kakao 등
    provider_user_id = Column(String(100), nullable=False)  # OAuth provider의 user id
    email = Column(String(255), nullable=False)

    # provider + provider_user_id 조합은 유니크해야 함
    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uq_provider_user_id"),
    )

    # Relationships
    user = relationship("UserModel", back_populates="oauth_identities")
