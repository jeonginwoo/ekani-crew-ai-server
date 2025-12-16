from pydantic import BaseModel


class OAuthLoginUrlResponse(BaseModel):
    """OAuth 로그인 URL 응답"""

    url: str


class OAuthCallbackResponse(BaseModel):
    """OAuth 콜백 응답"""

    session_id: str
