import pytest
import uuid
from unittest.mock import AsyncMock

from app.shared.vo.mbti import MBTI
from app.match.domain.match_ticket import MatchTicket
from app.match.application.usecase.match_usecase import MatchUseCase
from tests.match.fixtures.fake_match_queue_adapter import FakeMatchQueueAdapter


@pytest.mark.asyncio
async def test_format_match_result_payload():
    """
    [MATCH-3] 매칭 성공 시, Chat 도메인으로 보내는 데이터 규격(JSON)이
    Success Criteria에 맞게 생성되는지 검증
    """
    # Given
    fake_queue = FakeMatchQueueAdapter()

    # ChatPort를 Mocking하여 전달된 데이터를 가로챕니다.
    mock_chat_port = AsyncMock()
    mock_chat_port.create_chat_room.return_value = True

    usecase = MatchUseCase(match_queue_port=fake_queue, chat_room_port=mock_chat_port)

    # 파트너 미리 등록 (INFP <-> ENFJ 천생연분)
    partner = MatchTicket("partner_enfj", MBTI("ENFJ"))
    await fake_queue.enqueue(partner)

    # When: 매칭 요청
    my_id = "me_infp"
    my_mbti = MBTI("INFP")
    result = await usecase.request_match(my_id, my_mbti, level=1)

    # Then 1: UseCase 응답에 roomId가 포함되어야 함
    assert result["status"] == "matched"
    assert "roomId" in result
    assert len(result["roomId"]) > 0

    # Then 2: ChatPort가 호출되었는지 확인
    mock_chat_port.create_chat_room.assert_called_once()

    # Then 3: 전달된 Payload 데이터 규격 검증 (핵심)
    # call_args[0][0]은 첫 번째 호출의 첫 번째 인자(match_payload)입니다.
    payload = mock_chat_port.create_chat_room.call_args[0][0]

    print(f"\n[Captured Payload]: {payload}")

    # 3-1. roomId는 UUID v4 형식이어야 함
    try:
        uuid_obj = uuid.UUID(payload["roomId"], version=4)
    except ValueError:
        pytest.fail("roomId is not a valid UUID v4")

    # 3-2. users 리스트 검증
    assert len(payload["users"]) == 2
    users = payload["users"]

    # 순서는 보장되지 않을 수 있으므로 ID 집합으로 확인
    user_ids = {u["userId"] for u in users}
    assert my_id in user_ids
    assert "partner_enfj" in user_ids

    # MBTI 정보 포함 확인
    assert any(u["mbti"] == "INFP" for u in users)
    assert any(u["mbti"] == "ENFJ" for u in users)

    # 3-3. Timestamp 존재 확인
    assert "timestamp" in payload