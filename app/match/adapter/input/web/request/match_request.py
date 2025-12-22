from pydantic import BaseModel, Field

class MatchRequest(BaseModel):
    user_id: str = Field(..., description="매칭을 요청하는 유저의 ID")
    mbti: str = Field(..., description="유저의 MBTI (예: INFP)")