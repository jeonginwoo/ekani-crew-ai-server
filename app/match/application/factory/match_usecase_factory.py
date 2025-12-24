from app.match.adapter.output.chat.chat_client_adapter import ChatClientAdapter
from app.match.application.usecase.match_usecase import MatchUseCase
from app.match.adapter.output.persistence.redis_match_queue_adapter import RedisMatchQueueAdapter
from config.redis import get_redis  # 설정 파일에서 Redis 클라이언트 가져오기


class MatchUseCaseFactory:
    @staticmethod
    def create() -> MatchUseCase:
        redis_client = get_redis()
        queue_adapter = RedisMatchQueueAdapter(redis_client)
        chat_adapter = ChatClientAdapter()

        return MatchUseCase(
            match_queue_port=queue_adapter,
            chat_room_port=chat_adapter
        )