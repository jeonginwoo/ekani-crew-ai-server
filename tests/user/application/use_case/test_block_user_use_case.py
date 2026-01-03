import pytest
from unittest.mock import Mock

from app.user.application.use_case.block_user_use_case import BlockUserUseCaseImpl
from app.user.domain.block import Block
from app.user.domain.user import User
from app.shared.vo.mbti import MBTI
from app.shared.vo.gender import Gender
import uuid


@pytest.fixture
def mock_block_repository():
    return Mock()


@pytest.fixture
def mock_user_repository():
    return Mock()


@pytest.fixture
def mock_deactivate_chat_room_use_case():
    return Mock()


@pytest.fixture
def block_user_use_case(mock_block_repository, mock_user_repository, mock_deactivate_chat_room_use_case):
    return BlockUserUseCaseImpl(
        block_repository=mock_block_repository,
        user_repository=mock_user_repository,
        deactivate_chat_room_use_case=mock_deactivate_chat_room_use_case
    )


class TestBlockUser:
    def test_block_user_successfully(self, block_user_use_case, mock_block_repository, mock_user_repository, mock_deactivate_chat_room_use_case):
        # given
        blocker_id = uuid.uuid4()
        blocked_id = uuid.uuid4()

        blocker = User(id=str(blocker_id), email="blocker@test.com", mbti=MBTI("INTJ"), gender=Gender("FEMALE"))
        blocked = User(id=str(blocked_id), email="blocked@test.com", mbti=MBTI("ENFP"), gender=Gender("MALE"))

        mock_user_repository.find_by_id.side_effect = [blocker, blocked]
        mock_block_repository.find_by_blocker_and_blocked.return_value = None

        # when
        block_user_use_case.block(blocker_id=blocker_id, blocked_id=blocked_id)

        # then
        mock_block_repository.save.assert_called_once()
        saved_block = mock_block_repository.save.call_args[0][0]
        assert isinstance(saved_block, Block)
        assert saved_block.blocker_id == blocker_id
        assert saved_block.blocked_id == blocked_id
        mock_deactivate_chat_room_use_case.execute.assert_called_once_with(user1_id=blocker_id, user2_id=blocked_id)

    def test_block_user_who_is_already_blocked(self, block_user_use_case, mock_block_repository, mock_user_repository, mock_deactivate_chat_room_use_case):
        # given
        blocker_id = uuid.uuid4()
        blocked_id = uuid.uuid4()

        blocker = User(id=str(blocker_id), email="blocker@test.com", mbti=MBTI("INTJ"), gender=Gender("FEMALE"))
        blocked = User(id=str(blocked_id), email="blocked@test.com", mbti=MBTI("ENFP"), gender=Gender("MALE"))

        mock_user_repository.find_by_id.side_effect = [blocker, blocked]
        mock_block_repository.find_by_blocker_and_blocked.return_value = Block(
            blocker_id=blocker_id, blocked_id=blocked_id
        )

        # when
        block_user_use_case.block(blocker_id=blocker_id, blocked_id=blocked_id)

        # then
        mock_block_repository.save.assert_not_called()
        mock_deactivate_chat_room_use_case.execute.assert_not_called()
