from dataclasses import dataclass
from urllib.parse import quote

import httpx

from config.settings import get_settings

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
GOOGLE_CALLBACK_PATH = "/auth/google/callback"


@dataclass
class GoogleAccessToken:
    """Google Access Token"""

    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str | None = None


class GoogleOAuthService:
    """Google OAuth2 서비스"""

    def get_authorization_url(self) -> str:
        """Google 로그인 URL 생성"""
        settings = get_settings()
        redirect_uri = quote(f"{settings.BASE_URL}{GOOGLE_CALLBACK_PATH}", safe="")
        scope = "openid email profile"

        return (
            f"{GOOGLE_AUTH_URL}"
            f"?client_id={settings.GOOGLE_CLIENT_ID}"
            f"&redirect_uri={redirect_uri}"
            f"&response_type=code"
            f"&scope={quote(scope)}"
        )

    def get_access_token(self, code: str) -> GoogleAccessToken:
        """Authorization code로 access token 획득"""
        settings = get_settings()

        response = httpx.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": f"{settings.BASE_URL}{GOOGLE_CALLBACK_PATH}",
                "grant_type": "authorization_code",
            },
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()

        return GoogleAccessToken(
            access_token=data["access_token"],
            token_type=data["token_type"],
            expires_in=data["expires_in"],
            refresh_token=data.get("refresh_token"),
        )

    def get_user_profile(self, access_token: GoogleAccessToken) -> dict:
        """Access token으로 사용자 프로필 조회"""
        response = httpx.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token.access_token}"},
            timeout=10.0,
        )
        response.raise_for_status()
        return response.json()
