import pytest
from unittest.mock import MagicMock
from uuid import uuid4, UUID
from datetime import datetime

from app.chat.application.port.rating_repository_port import RatingRepositoryPort
from app.chat.application.use_case.rate_user_use_case import RateUserUseCase
from app.chat.application.dto.rate_user_request import RateUserRequest
from app.chat.domain.rating import Rating

@pytest.fixture
def mock_rating_repo():
    return MagicMock(spec=RatingRepositoryPort)

@pytest.fixture
def mock_uuid_generator():
    # Let's mock the uuid4 function to have a predictable ID
    return MagicMock(return_value=UUID('a1b2c3d4-e5f6-7890-1234-567890abcdef'))

def test_rate_user_successfully(mock_rating_repo, mock_uuid_generator):
    """사용자 평가를 성공적으로 저장한다"""
    # Given
    mock_rating_repo.find_by_room_id_and_rater_id.return_value = None
    use_case = RateUserUseCase(
        rating_repo=mock_rating_repo, 
        uuid_generator=mock_uuid_generator
    )
    
    request = RateUserRequest(
        rater_id="user-A",
        rated_user_id="user-B",
        room_id="room-1",
        score=5,
        feedback="Excellent!"
    )

    # When
    use_case.execute(request)

    # Then
    mock_rating_repo.find_by_room_id_and_rater_id.assert_called_once_with(
        room_id="room-1", rater_id="user-A"
    )
    mock_rating_repo.save.assert_called_once()
    saved_rating = mock_rating_repo.save.call_args[0][0]
    
    assert isinstance(saved_rating, Rating)
    assert saved_rating.id == 'a1b2c3d4-e5f6-7890-1234-567890abcdef'
    assert saved_rating.rater_id == "user-A"
    assert saved_rating.rated_user_id == "user-B"
    assert saved_rating.room_id == "room-1"
    assert saved_rating.score == 5
    assert saved_rating.feedback == "Excellent!"


def test_rate_user_fails_if_already_rated(mock_rating_repo):
    """이미 평가한 경우 중복 평가를 방지한다"""
    # Given
    existing_rating = Rating(
        id=str(uuid4()),
        rater_id="user-A",
        rated_user_id="user-B",
        room_id="room-1",
        score=4,
        feedback="Good",
        created_at=datetime.now()
    )
    mock_rating_repo.find_by_room_id_and_rater_id.return_value = existing_rating
    # We don't need a uuid_generator here since it should fail before generating a UUID
    use_case = RateUserUseCase(rating_repo=mock_rating_repo, uuid_generator=MagicMock())

    request = RateUserRequest(
        rater_id="user-A",
        rated_user_id="user-B",
        room_id="room-1",
        score=5,
        feedback="Excellent!"
    )

    # When & Then
    with pytest.raises(ValueError, match="이미 이 채팅방에서 사용자를 평가했습니다"):
        use_case.execute(request)
    
    mock_rating_repo.find_by_room_id_and_rater_id.assert_called_once_with(
        room_id="room-1", rater_id="user-A"
    )
    mock_rating_repo.save.assert_not_called()
