from typing import Optional
from app.match.domain.match_ticket import MatchTicket
from app.match.domain.mbti_compatibility import MBTICompatibility
from app.match.application.port.output.match_queue_port import MatchQueuePort
from app.user.application.port.block_repository_port import BlockRepositoryPort
from app.shared.vo.mbti import MBTI


class MatchService:
    """
    매칭 탐색 알고리즘을 수행하는 애플리케이션 서비스
    """

    def __init__(self, match_queue_port: MatchQueuePort, block_repository: BlockRepositoryPort):
        self.match_queue = match_queue_port
        self.block_repository = block_repository

    async def find_partner(self, my_ticket: MatchTicket, level: int = 1) -> Optional[MatchTicket]:
        # 1. 레벨에 맞는 타겟 MBTI 리스트 확보
        target_mbti_values = [m.value for m in MBTICompatibility.get_targets(my_ticket.mbti.value, level)]

        if not target_mbti_values:
            return None

        # 2. [최적화] 대기자가 많은 순서대로 정렬된 리스트 받기
        sorted_targets = await self.match_queue.get_sorted_targets_by_size(target_mbti_values)

        # 3. 순차 탐색 (0명인 큐는 스킵)
        for mbti_str, count in sorted_targets:
            if count == 0:
                continue

            target_mbti = MBTI(mbti_str)
            
            # 큐에서 유효한 파트너를 찾을 때까지 반복
            while True:
                partner_ticket = await self.match_queue.dequeue(target_mbti)

                if not partner_ticket:
                    # 해당 MBTI 큐가 비었으면 다음 큐로 이동
                    break

                # 차단 관계 확인
                is_blocked_by_me = await self.block_repository.find_by_blocker_and_blocked(
                    blocker_id=my_ticket.user_id,
                    blocked_user_id=partner_ticket.user_id
                )
                i_am_blocked = await self.block_repository.find_by_blocker_and_blocked(
                    blocker_id=partner_ticket.user_id,
                    blocked_user_id=my_ticket.user_id
                )

                if not is_blocked_by_me and not i_am_blocked:
                    # 차단되지 않은 유효한 파트너를 찾았으므로 반환
                    return partner_ticket
                
                # 차단된 유저인 경우, 이 파트너는 건너뛰고 큐의 다음 유저를 계속 탐색
        
        return None