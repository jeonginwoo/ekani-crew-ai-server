import uuid

from app.auth.application.port.oauth_identity_repository_port import (
    OAuthIdentityRepositoryPort,
)
from app.auth.application.port.session_repository_port import SessionRepositoryPort
from app.auth.domain.oauth_identity import OAuthIdentity
from app.auth.domain.session import Session
from app.auth.infrastructure.oauth.google_oauth_service import GoogleOAuthService
from app.user.application.port.user_repository_port import UserRepositoryPort
from app.user.domain.user import User


class GoogleOAuthUseCase:
    """Google OAuth 로그인 유스케이스"""

    def __init__(
        self,
        service: GoogleOAuthService,
        user_repo: UserRepositoryPort,
        oauth_identity_repo: OAuthIdentityRepositoryPort,
        session_repo: SessionRepositoryPort,
    ):
        self._service = service
        self._user_repo = user_repo
        self._oauth_identity_repo = oauth_identity_repo
        self._session_repo = session_repo

    def get_authorization_url(self) -> str:
        """Google 로그인 URL 반환"""
        return self._service.get_authorization_url()

    def login(self, code: str) -> dict:
        """
        Google OAuth 로그인 처리.

        1. code로 access token 획득
        2. access token으로 프로필 조회
        3. User/OAuthIdentity 생성 또는 조회
        4. Session 생성
        5. session_id 반환
        """
        # 1. Access token 획득
        access_token = self._service.get_access_token(code)

        # 2. 프로필 조회
        profile = self._service.get_user_profile(access_token)
        email = profile.get("email")
        google_id = profile.get("sub")  # Google의 고유 사용자 ID

        # 3. OAuthIdentity 조회 또는 생성
        existing_identity = (
            self._oauth_identity_repo.find_by_provider_and_provider_user_id(
                provider="google", provider_user_id=google_id
            )
        )

        if existing_identity:
            # 기존 사용자
            user = self._user_repo.find_by_email(existing_identity.email)
        else:
            # 신규 사용자
            user = self._user_repo.find_by_email(email)
            if not user:
                user = User(id=str(uuid.uuid4()), email=email)
                self._user_repo.save(user)

            # OAuthIdentity 생성
            oauth_identity = OAuthIdentity(
                provider="google",
                provider_user_id=google_id,
                email=email,
            )
            self._oauth_identity_repo.save(oauth_identity)

        # 4. Session 생성
        session_id = str(uuid.uuid4())
        session = Session(session_id=session_id, user_id=user.id)
        self._session_repo.save(session)

        return {
            "session_id": session_id,
            "user_id": user.id,
            "email": email,
        }
