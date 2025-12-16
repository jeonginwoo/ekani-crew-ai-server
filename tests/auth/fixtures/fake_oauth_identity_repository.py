from app.auth.application.port.oauth_identity_repository_port import OAuthIdentityRepositoryPort
from app.auth.domain.oauth_identity import OAuthIdentity


class FakeOAuthIdentityRepository(OAuthIdentityRepositoryPort):
    """테스트용 Fake OAuthIdentity 저장소"""

    def __init__(self):
        self._identities: dict[str, OAuthIdentity] = {}

    def save(self, identity: OAuthIdentity) -> None:
        key = f"{identity.provider}:{identity.provider_user_id}"
        self._identities[key] = identity

    def find_by_provider_and_provider_user_id(
        self, provider: str, provider_user_id: str
    ) -> OAuthIdentity | None:
        key = f"{provider}:{provider_user_id}"
        return self._identities.get(key)
