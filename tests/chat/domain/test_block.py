import pytest
from datetime import datetime
from app.chat.domain.block import Block


def test_block_creates_with_required_fields():
    """필수 필드로 Block 객체를 생성할 수 있다"""
    # Given: 차단에 필요한 정보
    block_id = "block-123"
    blocker_id = "userA"
    blocked_user_id = "userB"
    created_at = datetime.now()

    # When: Block 객체를 생성하면
    block = Block(
        id=block_id,
        blocker_id=blocker_id,
        blocked_user_id=blocked_user_id,
        created_at=created_at
    )

    # Then: 정상적으로 생성되고 값을 조회할 수 있다
    assert block.id == block_id
    assert block.blocker_id == blocker_id
    assert block.blocked_user_id == blocked_user_id
    assert block.created_at == created_at


def test_block_rejects_empty_id():
    """빈 id를 거부한다"""
    # Given: 빈 block_id
    block_id = ""

    # When & Then: Block 생성 시 ValueError가 발생한다
    with pytest.raises(ValueError, match="Block id는 비어있을 수 없습니다"):
        Block(
            id=block_id,
            blocker_id="userA",
            blocked_user_id="userB"
        )


def test_block_rejects_empty_blocker_id():
    """빈 blocker_id를 거부한다"""
    # Given: 빈 blocker_id
    blocker_id = ""

    # When & Then: Block 생성 시 ValueError가 발생한다
    with pytest.raises(ValueError, match="Blocker id는 비어있을 수 없습니다"):
        Block(
            id="block-123",
            blocker_id=blocker_id,
            blocked_user_id="userB"
        )


def test_block_rejects_empty_blocked_user_id():
    """빈 blocked_user_id를 거부한다"""
    # Given: 빈 blocked_user_id
    blocked_user_id = ""

    # When & Then: Block 생성 시 ValueError가 발생한다
    with pytest.raises(ValueError, match="Blocked user id는 비어있을 수 없습니다"):
        Block(
            id="block-123",
            blocker_id="userA",
            blocked_user_id=blocked_user_id
        )


def test_block_rejects_self_block():
    """자기 자신을 차단하는 것을 거부한다"""
    # Given: blocker_id와 blocked_user_id가 동일
    user_id = "userA"

    # When & Then: Block 생성 시 ValueError가 발생한다
    with pytest.raises(ValueError, match="자기 자신을 차단할 수 없습니다"):
        Block(
            id="block-123",
            blocker_id=user_id,
            blocked_user_id=user_id
        )


def test_block_auto_generates_created_at_if_not_provided():
    """created_at이 제공되지 않으면 자동으로 생성한다"""
    # Given: created_at 없이 차단 정보
    block_id = "block-123"

    # When: created_at 없이 Block을 생성하면
    block = Block(
        id=block_id,
        blocker_id="userA",
        blocked_user_id="userB"
    )

    # Then: created_at이 자동으로 설정된다
    assert isinstance(block.created_at, datetime)
