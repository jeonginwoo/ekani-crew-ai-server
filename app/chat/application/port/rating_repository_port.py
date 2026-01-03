from abc import ABC, abstractmethod

from app.chat.domain.rating import Rating


class RatingRepositoryPort(ABC):
    @abstractmethod
    def save(self, rating: Rating) -> None:
        ...

    @abstractmethod
    def find_by_room_id_and_rater_id(self, room_id: str, rater_id: str) -> Rating | None:
        ...
