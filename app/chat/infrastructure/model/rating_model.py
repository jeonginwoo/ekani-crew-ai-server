from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from config.database import Base

class RatingModel(Base):
    __tablename__ = "ratings"

    id = Column(String(36), primary_key=True)
    rater_id = Column(String(255), ForeignKey("users.id"), nullable=False, index=True)
    rated_user_id = Column(String(255), ForeignKey("users.id"), nullable=False, index=True)
    room_id = Column(String(36), ForeignKey("chat_rooms.id"), nullable=False, index=True)
    score = Column(Integer, nullable=False)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False)

    # Relationships
    rater = relationship("UserModel", foreign_keys=[rater_id])
    rated_user = relationship("UserModel", foreign_keys=[rated_user_id])
    room = relationship("ChatRoomModel", foreign_keys=[room_id])
