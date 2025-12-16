class OAuthIdentity:
    """OAuth provider 인증 정보를 담는 도메인 객체"""

    _VALID_PROVIDERS = ["google", "kakao"]

    def __init__(self, provider: str, provider_user_id: str, email: str):
        self._validate(provider, provider_user_id, email)
        self.provider = provider
        self.provider_user_id = provider_user_id
        self.email = email

    def _validate(self, provider: str, provider_user_id: str, email: str) -> None:
        """OAuthIdentity 값의 유효성을 검증한다"""
        if not provider:
            raise ValueError("provider는 비어있을 수 없습니다")
        if provider not in self._VALID_PROVIDERS:
            valid_providers = "/".join(self._VALID_PROVIDERS)
            raise ValueError(f"provider는 {valid_providers} 중 하나여야 합니다: {provider}")
        if not provider_user_id:
            raise ValueError("provider_user_id는 비어있을 수 없습니다")
        if not email:
            raise ValueError("email은 비어있을 수 없습니다")
