import pytest
from datetime import datetime
from app.chat.domain.rating import Rating

def test_rating_can_be_created():
    """Rating 도메인 모델을 생성할 수 있다."""
    # Given: 평가 데이터
    rating_id = "rating-uuid-123"
    rater_id = "user-A"
    rated_user_id = "user-B"
    room_id = "room-uuid-456"
    score = 5
    feedback = "Great conversation!"
    created_at = datetime.now()

    # When: Rating 객체를 생성하면
    rating = Rating(
        id=rating_id,
        rater_id=rater_id,
        rated_user_id=rated_user_id,
        room_id=room_id,
        score=score,
        feedback=feedback,
        created_at=created_at,
    )

    # Then: 객체가 올바르게 생성되고 속성 값을 가진다
    assert rating.id == rating_id
    assert rating.rater_id == rater_id
    assert rating.rated_user_id == rated_user_id
    assert rating.room_id == room_id
    assert rating.score == score
    assert rating.feedback == feedback
    assert rating.created_at == created_at

@pytest.mark.parametrize("invalid_score", [0, 6, -1])
def test_rating_rejects_invalid_score(invalid_score):
    """1-5점 범위를 벗어난 점수를 거부한다"""
    # Given: 유효하지 않은 점수
    # When & Then: Rating 생성 시 ValueError가 발생한다
    with pytest.raises(ValueError, match="점수는 1에서 5 사이여야 합니다"):
        Rating(
            id="rating-1",
            rater_id="user-A",
            rated_user_id="user-B",
            room_id="room-1",
            score=invalid_score,
            feedback="feedback",
        )

def test_rating_accepts_valid_score():
    """1-5점 범위의 유효한 점수를 허용한다"""
    # Given: 유효한 점수
    for valid_score in range(1, 6):
        # When: Rating 객체를 생성하면
        rating = Rating(
            id=f"rating-{valid_score}",
            rater_id="user-A",
            rated_user_id="user-B",
            room_id="room-1",
            score=valid_score,
            feedback="feedback",
        )
        # Then: 정상적으로 생성된다
        assert rating.score == valid_score

def test_rating_rejects_empty_rater_id():
    """빈 rater_id를 거부한다"""
    with pytest.raises(ValueError, match="rater_id는 비어있을 수 없습니다"):
        Rating(
            id="rating-1",
            rater_id="",
            rated_user_id="user-B",
            room_id="room-1",
            score=5,
            feedback="feedback",
        )

def test_rating_rejects_empty_rated_user_id():
    """빈 rated_user_id를 거부한다"""
    with pytest.raises(ValueError, match="rated_user_id는 비어있을 수 없습니다"):
        Rating(
            id="rating-1",
            rater_id="user-A",
            rated_user_id="",
            room_id="room-1",
            score=5,
            feedback="feedback",
        )

def test_rating_rejects_empty_room_id():
    """빈 room_id를 거부한다"""
    with pytest.raises(ValueError, match="room_id는 비어있을 수 없습니다"):
        Rating(
            id="rating-1",
            rater_id="user-A",
            rated_user_id="user-B",
            room_id="",
            score=5,
            feedback="feedback",
        )
