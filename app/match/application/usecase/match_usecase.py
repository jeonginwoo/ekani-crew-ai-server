from app.shared.vo.mbti import MBTI
from app.match.domain.match_ticket import MatchTicket
from app.match.application.port.output.match_queue_port import MatchQueuePort

from app.shared.vo.mbti import MBTI
from app.match.domain.match_ticket import MatchTicket
from app.match.application.port.output.match_queue_port import MatchQueuePort


class MatchUseCase:
    def __init__(self, match_queue_port: MatchQueuePort):
        self.match_queue = match_queue_port

    async def request_match(self, user_id: str, mbti: MBTI) -> dict:
        """
        유저의 매칭 요청을 처리합니다 (Enqueue).
        """
        # 1. 도메인 객체 생성
        ticket = MatchTicket(user_id=user_id, mbti=mbti)

        # 2. 큐에 추가 (Redis IO 발생 -> await 필수!)
        try:
            # 중복일 경우 Adapter에서 ValueError 발생
            await self.match_queue.enqueue(ticket)
            message = "매칭 대기열에 등록되었습니다."
            status = "waiting"

        except ValueError:
            # 이미 등록된 유저인 경우 (에러가 아니라 정상 응답처럼 처리)
            message = "이미 대기열에 등록된 유저입니다."
            status = "already_waiting"

        # 3. 현재 대기 상태 조회 (Redis IO 발생 -> await 필수!)
        wait_count = await self.get_waiting_count(mbti)

        return {
            "status": status,
            "message": message,
            "my_mbti": mbti.value,
            "wait_count": wait_count
        }

    async def cancel_match(self, user_id: str, mbti: MBTI) -> dict:
        """
        매칭 요청을 취소합니다 (Remove).
        """
        # Redis IO 발생 -> await 필수!
        is_removed = await self.match_queue.remove(user_id, mbti)

        if is_removed:
            return {"status": "cancelled", "message": "매칭이 취소되었습니다."}
        else:
            return {"status": "fail", "message": "대기열에서 유저를 찾을 수 없습니다."}

    async def get_waiting_count(self, mbti: MBTI) -> int:
        """
        특정 MBTI 큐의 대기 인원을 조회합니다.
        """
        return await self.match_queue.get_queue_size(mbti)